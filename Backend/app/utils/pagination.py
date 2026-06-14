from typing import Generic, TypeVar
from pydantic import BaseModel
from math import ceil

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int


def paginate(items: list, total: int, page: int, size: int) -> dict:
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": ceil(total / size) if size > 0 else 0,
    }
