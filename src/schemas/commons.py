from typing import Optional

from pydantic import BaseModel, ConfigDict


class BasePagination(BaseModel):
    prev_page: Optional[str] = None
    next_page: Optional[str] = None
    total_pages: int
    total_items: int
    model_config = ConfigDict(from_attributes=True)
