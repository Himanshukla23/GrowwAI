from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


class SemanticSearchService:
    """
    Lightweight semantic-ish search using TF-IDF embeddings + cosine similarity.
    """

    def __init__(self) -> None:
        self._vectorizer = TfidfVectorizer(stop_words="english")
        self._matrix = None
        self._index_ids: list[int] = []
        self._fitted = False

    def _build_text(self, df: pd.DataFrame) -> pd.Series:
        return (
            df["name"].astype(str)
            + " | "
            + df["cuisine"].astype(str)
            + " | "
            + df["location"].astype(str)
            + " | "
            + df["cost"].astype(str)
        )

    def fit(self, df: pd.DataFrame) -> None:
        if df.empty:
            self._fitted = False
            self._matrix = None
            self._index_ids = []
            return

        text_corpus = self._build_text(df).tolist()
        self._matrix = self._vectorizer.fit_transform(text_corpus)
        self._index_ids = df.index.tolist()
        self._fitted = True

    def score(self, query: str, df: pd.DataFrame) -> pd.Series:
        if df.empty or not query.strip():
            return pd.Series(0.0, index=df.index)

        self.fit(df)
        if not self._fitted or self._matrix is None:
            return pd.Series(0.0, index=df.index)

        query_vec = self._vectorizer.transform([query])
        sim = linear_kernel(query_vec, self._matrix).flatten()
        sim = np.clip(sim, 0.0, 1.0)
        return pd.Series(sim, index=df.index)
