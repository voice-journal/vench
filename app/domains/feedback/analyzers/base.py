# app/domains/feedback/analyzers/base.py
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

from app.domains.feedback.models import FeedbackAnalysisStatus


@dataclass(frozen=True)
class AnalyzerResult:
    status: FeedbackAnalysisStatus
    keywords: List[str]
    model_version: str


class FeedbackTextAnalyzer(Protocol):
    def analyze(self, comment: str) -> AnalyzerResult:
        ...