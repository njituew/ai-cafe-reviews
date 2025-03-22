import matplotlib.pyplot as plt
from io import BytesIO
from aiogram.types import BufferedInputFile


async def test_graph() -> BytesIO:
    x = [1, 2, 3, 4, 5]
    y = [10, 20, 25, 30, 40]
    plt.figure(figsize=(6, 4))
    plt.plot(x, y, marker='o')
    plt.title("test")
    plt.xlabel("X")
    plt.ylabel("Y")

    # тут мы сохраняем график в буфер (чтобы не делать файлик)
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)  # сбрасываем указатель в 0 чтобы потом прочитать файл с начала
    plt.close()
    
    # возвращаем байтики в буфере
    return buffer