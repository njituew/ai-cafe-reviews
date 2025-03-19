reviews = [
        {"review_id": 1, "user_id": 1, "mark": 5, "text": "Отлично!", "tonality": 1, "readed": False},
        {"review_id": 2, "user_id": 2, "mark": 4, "text": "Хорошо!", "tonality": 1, "readed": False},
        {"review_id": 3, "user_id": 3, "mark": 3, "text": "Нормально!", "tonality": 0, "readed": False},
        {"review_id": 4, "user_id": 4, "mark": 2, "text": "Плохо!", "tonality": -1, "readed": False},
        {"review_id": 5, "user_id": 5, "mark": 1, "text": "Ужасно!", "tonality": -1, "readed": False},
        {"review_id": 6, "user_id": 6, "mark": 3, "text": "Нормально!", "tonality": 0, "readed": False},
        {"review_id": 7, "user_id": 6, "mark": 3, "text": "Нормально!", "tonality": 0, "readed": False},
        {"review_id": 8, "user_id": 6, "mark": 3, "text": "Нормально!", "tonality": 0, "readed": False},
        {"review_id": 9, "user_id": 6, "mark": 3, "text": "Нормально!", "tonality": 0, "readed": False},
        {"review_id": 10, "user_id": 6, "mark": 3, "text": "Нормально!", "tonality": 0, "readed": False},
        {"review_id": 11, "user_id": 6, "mark": 3, "text": "Нормально!", "tonality": 0, "readed": False},
        {"review_id": 12, "user_id": 6, "mark": 3, "text": "Нормально!", "tonality": 0, "readed": False},
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
