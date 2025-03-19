def get_unreaded_reviews(start: int = 0, end: int = 0) -> list[dict]:
    reviews = [
        {"review_id": 1, "user_id": 1, "mark": 5, "text": "Отлично!", "tonality": 1, "readed": False},
        {"review_id": 2, "user_id": 2, "mark": 4, "text": "Хорошо!", "tonality": 1, "readed": False},
        {"review_id": 3, "user_id": 3, "mark": 3, "text": "Нормально!", "tonality": 0, "readed": False},
        {"review_id": 4, "user_id": 4, "mark": 2, "text": "Плохо!", "tonality": -1, "readed": False},
        {"review_id": 5, "user_id": 5, "mark": 1, "text": "Ужасно!", "tonality": -1, "readed": False},
        {"review_id": 6, "user_id": 6, "mark": 3, "text": "Нормально!", "tonality": 0, "readed": False},
        {"review_id": 6, "user_id": 6, "mark": 3, "text": "Нормально!", "tonality": 0, "readed": False},
        {"review_id": 6, "user_id": 6, "mark": 3, "text": "Нормально!", "tonality": 0, "readed": False},
        {"review_id": 6, "user_id": 6, "mark": 3, "text": "Нормально!", "tonality": 0, "readed": False},
        {"review_id": 6, "user_id": 6, "mark": 3, "text": "Нормально!", "tonality": 0, "readed": False},
        {"review_id": 6, "user_id": 6, "mark": 3, "text": "Нормально!", "tonality": 0, "readed": False},
        {"review_id": 6, "user_id": 6, "mark": 3, "text": "Нормально!", "tonality": 0, "readed": False},
    ]
    for i in range(1, len(reviews)):
        reviews[i]["review_id"], reviews[i]["user_id"] = i+1, i+1
    return reviews