from fastapi import Query


class PaginationParams:  # noqa: B903
    def __init__(
        self,
        page_number: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
    ) -> None:
        self.page_number = page_number
        self.page_size = page_size
