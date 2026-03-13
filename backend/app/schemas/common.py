from pydantic import BaseModel, Field


class DataProvenance(BaseModel):
    data_source: str = Field(default="postgres")
    is_fallback: bool = Field(default=False)
    data_complete: bool = Field(default=True)
    note: str | None = None
