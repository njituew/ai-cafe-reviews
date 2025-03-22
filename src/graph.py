import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # неинтерактивный бэкенд

import matplotlib.pyplot as plt
from io import BytesIO


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
