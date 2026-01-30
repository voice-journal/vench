from __future__ import annotations

from collections import Counter
from typing import List

import regex as re
from kiwipiepy import Kiwi

from app.domains.feedback.analyzers.base import AnalyzerResult, FeedbackTextAnalyzer
from app.domains.feedback.models import FeedbackAnalysisStatus


DEFAULT_STOPWORDS = {
    "너무", "진짜", "정말", "그냥", "근데", "그리고", "이거", "저거", "거", "좀",
    "같다", "하다", "되다", "있다", "없다", "이다", "것", "수", "때", "듯", "처럼",
    "요", "에서", "으로", "에게", "하고", "하면", "했는데", "하는데",
}

# 반복 문자 축약 (ㅋㅋㅋㅋ, ㅠㅠㅠ 등)
_RE_REPEAT = re.compile(r"(.)\1{2,}")
_RE_NON_TEXT = re.compile(r"[^\p{Hangul}\p{Latin}\p{Number}\s]+")


class KiwiAnalyzer(FeedbackTextAnalyzer):
    def __init__(self, top_n: int = 3, model_version: str = "morph-v1"):
        self._kiwi = Kiwi()
        self._top_n = top_n
        self._model_version = model_version

    def _normalize(self, text: str) -> str:
        t = text.strip()
        t = _RE_REPEAT.sub(r"\1\1", t)
        t = _RE_NON_TEXT.sub(" ", t)
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def _extract_tokens(self, text: str) -> List[str]:
        # 명사/형용사 위주로 추출
        tokens: List[str] = []
        for token, pos, _, _ in self._kiwi.analyze(text)[0][0]:
            # Kiwi POS 예: NNG/NNP/VA 등. 넓게 잡되, 과한 동사는 제외.
            if pos.startswith("N") or pos == "VA":
                w = str(token).strip()
                if len(w) < 2:
                    continue
                if w in DEFAULT_STOPWORDS:
                    continue
                tokens.append(w)
        return tokens

    def analyze(self, comment: str) -> AnalyzerResult:
        norm = self._normalize(comment or "")
        if not norm:
            return AnalyzerResult(status=FeedbackAnalysisStatus.SKIPPED, keywords=[], model_version=self._model_version)

        # 너무 짧으면 스킵
        if len(norm) < 4:
            return AnalyzerResult(status=FeedbackAnalysisStatus.SKIPPED, keywords=[], model_version=self._model_version)

        tokens = self._extract_tokens(norm)
        if not tokens:
            return AnalyzerResult(status=FeedbackAnalysisStatus.SKIPPED, keywords=[], model_version=self._model_version)

        counts = Counter(tokens)
        keywords = [w for w, _ in counts.most_common(self._top_n)]
        return AnalyzerResult(status=FeedbackAnalysisStatus.DONE, keywords=keywords, model_version=self._model_version)
