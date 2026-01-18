from __future__ import annotations

import datetime
from pydantic import BaseModel


class UserHistory(BaseModel):

    runid: float | None = None
    job_id: float | None = None
    id: str
    user: str
    status: str
    event_time: datetime.datetime = datetime.datetime.now()
    comment: str = 'none'
    event_time2: datetime.datetime = datetime.datetime.now()
