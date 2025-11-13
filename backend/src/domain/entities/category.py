from dataclasses import dataclass

@dataclass
class Category:
    id: int | None
    name: str
    user_id: int | None = None  # optional if categories are user-specific
