from datetime import datetime

from pydantic import BaseModel


class DigestEntry(BaseModel):
    title: str
    source: str
    link: str
    published_at: datetime
