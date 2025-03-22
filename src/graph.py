import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # неинтерактивный бэкенд

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO

from datetime import date, timedelta


async def distribution_of_ratings(list_of_ratings: list[int]) -> BytesIO:
    """
    Показывает сколько отзывов имеет конкретную оценку

    Args:
        list_of_ratings (list[int]): список, где индекс - это оценка (-1), значение - количество отзывов с такой оценкой.
    """
    x = [i + 1 for i in range(len(list_of_ratings))]
    y = list_of_ratings

    sns.set_style("darkgrid")

    plt.figure(figsize=(6, 4))
    sns.barplot(x=x, y=y, hue=x, legend=False, palette="crest")

    plt.title("График распределения оценок")
    plt.xlabel("Оценка")
    plt.ylabel("Количество отзывов")

    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)  # сбрасываем указатель в 0 чтобы потом прочитать файл с начала
    plt.close()

    return buffer

async def changes_of_average_grade(list_of_grades: list[float]) -> BytesIO:
    """
    Показывает как изменялась средняя оценка со временем.
    Период расчётов - последние k дней, где k - длина списка.

    Args:
        list_of_grades (list[int]): список, где индекс - это дата, значение - средняя оценка в этот день.
    """
    end_date = date.today() 
    start_date = end_date - timedelta(days=len(list_of_grades))
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

# UwU