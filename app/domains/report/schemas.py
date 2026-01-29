from typing import Dict
from pydantic import BaseModel

class WeeklyReportResponse(BaseModel):
    # 예: {"기쁨": 3, "슬픔": 1, ...}
    statistics: Dict[str, int]
