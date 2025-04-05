import sys
import random

# Задание 3.12
# 1. Считать массив A из параметров командной строки (10 целых чисел)
# 2. Найти и вывести наименьший нечетный элемент массива A
# 3. Создать массив B из 10 случайных целых чисел
# 4. Поменять местами массивы A и B
# 5. Вывести оба массива

# 1. Чтение массива A из аргументов командной строки
if len(sys.argv) != 11:
    print("Ошибка: требуется 10 целочисленных аргументов")
    sys.exit(1)

try:
    array_a = [int(arg) for arg in sys.argv[1:11]]
except ValueError:
    print("Ошибка: все аргументы должны быть целыми числами")
    sys.exit(1)

# 2. Поиск наименьшего нечетного элемента
min_odd = None
for num in array_a:
    if num % 2 != 0:  # Проверка на нечетность
        if min_odd is None or num < min_odd:
            min_odd = num

if min_odd is not None:
    print(f"Наименьший нечетный элемент массива A: {min_odd}")
else:
    print("В массиве A нет нечетных элементов")

# 3. Создание массива B из случайных чисел
array_b = [random.randint(0, 100) for _ in range(10)]
print("Исходный массив B:", array_b)

# 4. Обмен массивами A и B
array_a, array_b = array_b, array_a

# 5. Вывод результатов
print("\nПосле обмена:")
print("Массив A:", array_a)
print("Массив B:", array_b)


