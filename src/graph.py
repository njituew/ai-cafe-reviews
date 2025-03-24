import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # неинтерактивный бэкенд

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from db.utils import get_reviews_by_time
from io import BytesIO
from datetime import date, timedelta, datetime
from pytz import timezone


async def distribution_of_ratings() -> BytesIO:
    """
    Показывает сколько отзывов имеет конкретную оценку.
    """
    list_of_ratings = [0] * 5
    list_of_reviews = await get_reviews_by_time(datetime(1, 1, 1, 0, 0, 0), datetime.now(MOSCOW_TZ))
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


async def dynamics_of_satisfaction() -> BytesIO:
    """
    Показывает как изменялась средняя оценка за последний месяц.
    """
    global MOSCOW_TZ
    start_date = datetime.now(MOSCOW_TZ) - timedelta(days=30)

    x = [start_date + timedelta(days = i + 1) for i in range(30)]
    y = []
    sum_of_all = 0
    len_of_all = 0
    for day in x:
        cur_sum, cur_len = await calculate_day(day)
        sum_of_all += cur_sum
        len_of_all += cur_len
        if len_of_all > 0:
            y.append(sum_of_all / len_of_all)
        else:
            y.append(0)

    sns.set_style("darkgrid")

    plt.figure(figsize=(10, 6))
    sns.lineplot(x=x, y=y, marker="o")

    plt.ylim(bottom=0)
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


MOSCOW_TZ = timezone('Europe/Moscow')
async def calculate_day(day: date):
    start = datetime(day.year, day.month, day.day, 0, 0, 0)
    end = datetime(day.year, day.month, day.day, 23, 59, 59)

    # Запрос отзывов за указанный день в UTC+3
    reviews = await get_reviews_by_time(start, end)
    sum_of_ratings = 0
    for review in reviews:
        sum_of_ratings += review.rating
    return sum_of_ratings, len(reviews)


async def number_of_reviews() -> BytesIO:
    """
    Показывает сколько отзывов было в каждый день за последний месяц.
    """
    global MOSCOW_TZ
    start_date = datetime.now(MOSCOW_TZ) - timedelta(days=30)

    x = [start_date.date() + timedelta(days = i + 1) for i in range(30)]
    y = []

    for day in x:
        cur_len = len(await get_reviews_by_time(datetime(day.year, day.month, day.day, 0, 0, 0),  datetime(day.year, day.month, day.day, 23, 59, 59)))
        y.append(cur_len)
    
    sns.set_style("darkgrid")

    plt.figure(figsize=(10, 6))
    sns.barplot(x=x, y=y, hue=x, legend=False, palette="crest")

    plt.ylim(bottom=0)
    plt.title("График количества отзывов")
    plt.xlabel("Дата")
    plt.ylabel("Количество отзывов")
    plt.gca().yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)  # сбрасываем указатель в 0 чтобы потом прочитать файл с начала
    plt.close()

    return buffer
