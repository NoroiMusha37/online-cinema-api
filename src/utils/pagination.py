def paginate(items, count: int, page: int, size: int, path: str) -> dict:
    total_pages = (count + size - 1) // size
    return {
        "items": items,
        "prev_page": f"{path}?page={page - 1}&size={size}"
        if page > 1 else None,
        "next_page": f"{path}?page={page + 1}&size={size}"
        if page < total_pages else None,
        "total_pages": total_pages,
        "total_items": count,
    }