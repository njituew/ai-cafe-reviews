import random
from datetime import datetime, timedelta

reviews = [
    {
        "review_id": i,
        "user_id": i if i % 20 != 0 else 549991539, # вставь свой user_id
        "rating": random.randint(1, 5),
        "text": f"Тестовый отзыв {i}: {'вкусно' if random.random() > 0.5 else 'неплохо'}!",
        "tonality": random.choice(["Very Positive", "Positive", "Neutral", "Negative", "Very Negative"]),
        "readed": random.choice([True, False]),
        "date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%d.%m.%Y %H:%M")
    }
    for i in range(1, 101)
]

def get_review(id: int = 0) -> dict:
    """Возвращает отзыв по ID."""
    global reviews
    for review in reviews:
        if review["review_id"] == id:
            return review
    return {}


def get_user_reviews(user_id: int) -> list[dict]:
    """Возвращает все отзывы пользователя по его user_id."""
    global reviews
    return [r for r in reviews if r["user_id"] == user_id]


def delete_review_db(review_id: int) -> bool:
    """Удаляет отзыв по review_id, возвращает True при успехе."""
    global reviews
    for i, review in enumerate(reviews):
        if review["review_id"] == review_id:
            reviews.pop(i)
            return True
    return False
