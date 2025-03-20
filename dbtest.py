reviews = [
    {"review_id": i, "user_id": i % 10 + 1, "mark": (i % 5) + 1, "text": f"Тестовый отзыв {i}!", "tonality": (i % 3) - 1, "readed": False}
    for i in range(1, 101)
    ]


def get_unreaded_reviews(start: int = 0, end: int = 0) -> list[dict]:
    global reviews
    return reviews


def get_review(id: int = 0) -> dict:
    global reviews
    for review in reviews:
        if review["review_id"] == id:
            return review
    return {}
