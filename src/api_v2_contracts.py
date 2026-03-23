from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from src.api_payload_utils import PayloadShape, normalize_bool_flag

VALID_USERS = {"andreas", "karen"}
VALID_CONTEXTS = {"private", "executive"}  # wardrobe usage context

API_V2_ITEM_MUTATION_SHAPE = PayloadShape(
    allowed_fields=(
        "user_id",
        "name",
        "brand",
        "category",
        "color_primary",
        "color_variant",
        "needs_review",
        "material_main",
        "fit",
        "collar",
        "price",
        "vision_description",
        "image_path",
        "context",
        "size",
        "notes",
    ),
    required_fields=("user_id", "name"),
    normalizers={"needs_review": normalize_bool_flag},
)


class ItemCreateRequest(BaseModel):
    user_id: str = Field(..., description="andreas|karen")
    name: str
    brand: Optional[str] = None
    category: Optional[str] = None
    color_primary: Optional[str] = None
    color_variant: Optional[str] = None
    material_main: Optional[str] = None
    fit: Optional[str] = None
    collar: Optional[str] = None
    price: Optional[str] = None
    vision_description: Optional[str] = None
    context: Optional[str] = None  # private|executive
    size: Optional[str] = None
    notes: Optional[str] = None
    image_main_base64: str = Field(..., description="Base64 or data URL")
    image_ext: Optional[str] = Field(None, description="jpg|png|webp etc; server stores main.jpg")


class ItemUpdateRequest(BaseModel):
    user_id: Optional[str] = None
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    color_primary: Optional[str] = None
    color_variant: Optional[str] = None
    material_main: Optional[str] = None
    fit: Optional[str] = None
    collar: Optional[str] = None
    price: Optional[str] = None
    vision_description: Optional[str] = None
    needs_review: Optional[int] = None
    context: Optional[str] = None
    size: Optional[str] = None
    notes: Optional[str] = None


class ItemSummary(BaseModel):
    id: int
    name: str
    category: Optional[str]
    color_primary: Optional[str]
    color_variant: Optional[str] = None
    needs_review: int = 0
    context: Optional[str] = None


class ListItemsResponse(BaseModel):
    user: str
    items: List[ItemSummary]


class ItemResponse(BaseModel):
    id: int
    user_id: str
    name: str
    brand: Optional[str]
    category: Optional[str]
    color_primary: Optional[str]
    color_variant: Optional[str] = None
    needs_review: int = 0
    material_main: Optional[str]
    fit: Optional[str]
    collar: Optional[str]
    price: Optional[str]
    vision_description: Optional[str]
    image_path: Optional[str]
    created_at: str
    context: Optional[str] = None
    size: Optional[str] = None
    notes: Optional[str] = None
    main_image_url: Optional[str] = None
    image_urls: List[str] = Field(default_factory=list)


class DeleteResponse(BaseModel):
    deleted: bool
    id: int
    image_path: str


class ReviewItem(BaseModel):
    id: int
    name: str
    category: Optional[str]
    color_primary: Optional[str]
    color_variant: Optional[str]
    needs_review: int
    suggestions: List[str] = Field(default_factory=list)


class ReviewQueueResponse(BaseModel):
    user: str
    total: int
    items: List[ReviewItem]
