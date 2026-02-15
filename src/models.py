from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class StyleGoals(BaseModel):
    strategy: str = "Minimalist Capsule"
    max_items_total: int = 50
    min_outfit_days: int = Field(14, description="Ziel: Outfits für X Tage")
    review_period_months: int = Field(12, description="Aussortier-Zyklus")
    sustainability_weight: float = Field(0.8, description="Priorität von Nachhaltigkeit (0-1)")
    preferred_materials: List[str] = []

class PhysicalProfile(BaseModel):
    height_cm: Optional[int] = None
    color_type: Optional[str] = Field(None, description="z.B. Cool Summer")
    body_shape: Optional[str] = None # Wird später via KI-Bildanalyse gefüllt

class DiscardEntry(BaseModel):
    item_id: str
    reason: str 
    date_discarded: datetime = Field(default_factory=datetime.now)

class UserProfile(BaseModel):
    user_id: str
    name: str
    physical: PhysicalProfile
    goals: StyleGoals
    preferences: List[str] = []
    discard_history: List[DiscardEntry] = []