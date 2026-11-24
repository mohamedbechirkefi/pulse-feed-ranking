# SPDX-License-Identifier: LicenseRef-PULSE-NC-Research-1.0
"""MovieLens 1M ingestion (research/protocol.md sections 15.2 to 15.6).

Pure functions from the raw text of ``movies.dat`` and ``ratings.dat`` to aggregates and
preference vectors. ``users.dat`` is never read. No function returns or writes a user id:
preference vectors are ordered by user id but carry no id.
"""
from __future__ import annotations

import re
import zipfile
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

# The 18 genres listed in the MovieLens 1M README.
GENRES = (
    "Action", "Adventure", "Animation", "Children's", "Comedy", "Crime", "Documentary", "Drama",
    "Fantasy", "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War",
    "Western",
)
LIKE_THRESHOLD = 4  # like := rating >= 4 (section 15.2)
MAX_BAD_SHARE = 0.01  # stop if more than 1% of a file's rows fail the schema
_INT = re.compile(r"^[0-9]+$")


class IngestError(ValueError):
    """Schema failure rate above the protocol limit, or an empty input."""


@dataclass
class Ingested:
    topics: list[str]  # K genres, in topic-index order (most movies first)
    genre_movie_counts: dict[str, int]
    movie_topic: dict[int, int]  # included movie id -> primary topic index
    pi: np.ndarray  # (K,) share of included movies per primary topic
    counts: dict[str, int] = field(default_factory=dict)  # rows read, excluded by reason
    like_rate_calibration: float = float("nan")  # L*, section 15.4
    prefs_calibration: np.ndarray = field(default_factory=lambda: np.zeros((0, 0)))  # odd user ids
    prefs_heldout: np.ndarray = field(default_factory=lambda: np.zeros((0, 0)))  # even user ids


def parse_movies(text: str) -> tuple[dict[int, tuple[str, ...]], int, int]:
    """Returns ({movie_id: genres}, rows, bad_rows)."""
    out: dict[int, tuple[str, ...]] = {}
    rows = bad = 0
    for line in text.splitlines():
        if not line.strip():
            continue
        rows += 1
        parts = line.split("::")
        if len(parts) != 3 or not _INT.match(parts[0]):
            bad += 1
            continue
        genres = tuple(parts[2].split("|"))
        mid = int(parts[0])
        if not genres or any(g not in GENRES for g in genres) or len(set(genres)) != len(genres) or mid in out:
            bad += 1
            continue
        out[mid] = genres
    return out, rows, bad


def parse_ratings(text: str) -> tuple[np.ndarray, int, int]:
    """Returns (array (n, 3) of user id, movie id, rating), rows, bad_rows. Timestamps are not kept."""
    recs: list[tuple[int, int, int]] = []
    rows = bad = 0
    for line in text.splitlines():
        if not line.strip():
            continue
        rows += 1
        parts = line.split("::")
        if len(parts) != 4 or not all(_INT.match(p) for p in parts):
            bad += 1
            continue
        u, m, r = int(parts[0]), int(parts[1]), int(parts[2])
        if not 1 <= r <= 5 or u < 1 or m < 1:
            bad += 1
            continue
        recs.append((u, m, r))
    arr = np.array(recs, dtype=np.int64).reshape(-1, 3)
    return arr, rows, bad


def choose_topics(movies: dict[int, tuple[str, ...]], k: int = 10) -> tuple[list[str], dict[str, int]]:
    """The k genres with the most movies; ties alphabetical (section 15.2)."""
    cnt = Counter(g for gs in movies.values() for g in gs)
    ranked = sorted(cnt, key=lambda g: (-cnt[g], g))
    if len(ranked) < k:
        raise IngestError(f"only {len(ranked)} genres present, need {k}")
    return ranked[:k], dict(cnt)


def primary_topic(genres: tuple[str, ...], topics: list[str], cnt: dict[str, int]) -> int | None:
    """Among the movie's genres in the topic set, the one with the fewest movies; ties alphabetical."""
    cand = [g for g in genres if g in topics]
    if not cand:
        return None
    g = min(cand, key=lambda x: (cnt[x], x))
    return topics.index(g)


def preference_vectors(n_like: np.ndarray, pi: np.ndarray) -> np.ndarray:
    """p_u proportional to (n_uz + 1) / pi_z, rows normalised (section 15.6)."""
    if np.any(pi <= 0):
        raise IngestError("every topic needs at least one included movie")
    w = (n_like + 1.0) / pi[None, :]
    return w / w.sum(axis=1, keepdims=True)


def _check_bad(name: str, rows: int, bad: int) -> None:
    if rows == 0:
        raise IngestError(f"{name}: no rows")
    if bad / rows > MAX_BAD_SHARE:
        raise IngestError(f"{name}: {bad} of {rows} rows fail the schema (limit {MAX_BAD_SHARE:.0%})")


def ingest(movies_text: str, ratings_text: str, k: int = 10) -> Ingested:
    """Raw MovieLens text to topics, pi, L* and the two halves' preference vectors."""
    movies, m_rows, m_bad = parse_movies(movies_text)
    _check_bad("movies.dat", m_rows, m_bad)
    ratings, r_rows, r_bad = parse_ratings(ratings_text)
    _check_bad("ratings.dat", r_rows, r_bad)

    topics, gcnt = choose_topics(movies, k)
    movie_topic = {}
    for mid in sorted(movies):
        z = primary_topic(movies[mid], topics, gcnt)
        if z is not None:
            movie_topic[mid] = z
    pi = np.bincount(list(movie_topic.values()), minlength=k).astype(float)
    pi = pi / pi.sum()

    known = np.array([m in movies for m in ratings[:, 1]], dtype=bool)
    incl = np.array([m in movie_topic for m in ratings[:, 1]], dtype=bool)
    kept = ratings[incl]
    z = np.array([movie_topic[m] for m in kept[:, 1]], dtype=np.int64)
    like = kept[:, 2] >= LIKE_THRESHOLD
    odd = kept[:, 0] % 2 == 1

    all_users = np.unique(ratings[:, 0])
    users = np.unique(kept[:, 0])

    def half(mask: np.ndarray) -> np.ndarray:
        us = np.unique(kept[mask, 0])
        pos = {u: i for i, u in enumerate(us)}
        n = np.zeros((len(us), k))
        sel = mask & like
        np.add.at(n, (np.array([pos[u] for u in kept[sel, 0]], dtype=np.int64), z[sel]), 1.0)
        return preference_vectors(n, pi)

    res = Ingested(topics=topics, genre_movie_counts=gcnt, movie_topic=movie_topic, pi=pi)
    res.counts = {
        "movies_rows": m_rows, "movies_bad_rows": m_bad, "movies_valid": len(movies),
        "movies_excluded_no_topic": len(movies) - len(movie_topic), "movies_included": len(movie_topic),
        "ratings_rows": r_rows, "ratings_bad_rows": r_bad, "ratings_valid": int(len(ratings)),
        "ratings_excluded_unknown_movie": int((~known).sum()),
        "ratings_excluded_no_topic": int((known & ~incl).sum()),
        "ratings_included": int(len(kept)),
        "ratings_included_calibration": int(odd.sum()), "ratings_included_heldout": int((~odd).sum()),
        "users_valid": int(len(all_users)), "users_excluded_no_included_rating": int(len(all_users) - len(users)),
        "users_calibration": int(len(np.unique(kept[odd, 0]))), "users_heldout": int(len(np.unique(kept[~odd, 0]))),
    }
    res.like_rate_calibration = float(like[odd].mean()) if odd.any() else float("nan")
    res.prefs_calibration = half(odd)
    res.prefs_heldout = half(~odd)
    return res


def read_zip(path: Path) -> tuple[str, str]:
    """The text of ml-1m/movies.dat and ml-1m/ratings.dat (ISO-8859-1, as distributed)."""
    with zipfile.ZipFile(path) as zf:
        movies = zf.read("ml-1m/movies.dat").decode("latin-1")
        ratings = zf.read("ml-1m/ratings.dat").decode("latin-1")
    return movies, ratings

