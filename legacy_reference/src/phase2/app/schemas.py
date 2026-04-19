from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class RecommendationRequest(BaseModel):
    location: str = Field(..., min_length=1)
    budget: Literal["low", "medium", "high"] = Field(..., description="low | medium | high")
    cuisine: str = Field(..., min_length=1)
    min_rating: float = Field(..., ge=0, le=5)
    extra_preferences: Optional[str] = ""

    @field_validator("location", "cuisine", mode="before")
    @classmethod
    def normalize_text_fields(cls, value: str) -> str:
        return str(value).strip().lower()

    @field_validator("extra_preferences", mode="before")
    @classmethod
    def normalize_extra_preferences(cls, value: Optional[str]) -> str:
        return str(value or "").strip().lower()


class CandidateRestaurant(BaseModel):
    name: str
    location: str
    cuisine: str
    cost: str
    rating: float


class RecommendationItem(BaseModel):
    name: str
    location: str
    cuisine: str
    rating: float
    avg_cost: int
    cost: str
    reason: str


class RecommendationResponse(BaseModel):
    total_candidates: int
    returned_recommendations: int
    recommendations: List[RecommendationItem]
