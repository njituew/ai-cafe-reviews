import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # неинтерактивный бэкенд

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from db.utils import get_reviews_by_time
from io import BytesIO
from datetime import date, timedelta, datetime


async def distribution_of_ratings() -> BytesIO:
    """
    Показывает сколько отзывов имеет конкретную оценку

    Args:
        list_of_ratings (list[int]): список, где индекс - это оценка (-1), значение - количество отзывов с такой оценкой.
    """
    list_of_ratings = [0] * 5
    list_of_reviews = await get_reviews_by_time(datetime(1, 1, 1, 0, 0, 0), datetime.now())
    for review in list_of_reviews:
        list_of_ratings[review.rating - 1] += 1
    x = [i for i in range(1, 6)]

    sns.set_style("darkgrid")

    plt.figure(figsize=(6, 4))
    sns.barplot(x=x, y=list_of_ratings, hue=x, legend=False, palette="crest")

    plt.ylim(bottom=0)
    plt.title("График распределения оценок")
    plt.xlabel("Оценка")
    plt.ylabel("Количество отзывов")
    plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))  # Устанавливаем только целые числа на оси Y

    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)  # сбрасываем указатель в 0 чтобы потом прочитать файл с начала
    plt.close()

    return buffer


async def dynamics_of_satisfaction(list_of_grades: list[float]) -> BytesIO:
    """
    Показывает как изменялась средняя оценка со временем.
    Период расчётов - последние k дней, где k - длина списка.

    Args:
        list_of_grades (list[int]): список, где индекс - это день, значение - средняя оценка в этот день.
    """
    end_date = datetime.now()
    start_date = date.today() - timedelta(days=30)


    x = [start_date + timedelta(days = i + 1) for i in range((end_date - start_date).days)]
    y = list_of_grades

    sns.set_style("darkgrid")

    plt.figure(figsize=(6, 4))
    sns.lineplot(x=x, y=y, marker="o")

    plt.title("График изменения средней оценки")
    plt.xlabel("Дата")
    plt.ylabel("Средняя оценка")
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Только дата
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())  # Шаг — 1 день

    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    plt.close()

    return buffer
