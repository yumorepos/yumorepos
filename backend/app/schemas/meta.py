from pydantic import BaseModel


class MethodologyResponse(BaseModel):
    score_version: str
    metric_descriptions: dict[str, str]
    caveats: list[str]
    source_coverage_notes: list[str]
