# Задание 2.12
# 1. Считать с клавиатуры произвольную строку
# 2. Вывести все слова, которые оканчиваются на букву "u"
# Ограничения: нельзя использовать substr, upper, lower, split

# Считываем строку с клавиатуры
input_string = input("Введите произвольную строку: ")

current_word = ""  # Переменная для накопления текущего слова
words_with_u = []  # Список для хранения слов, оканчивающихся на 'u'

# Проходим по каждому символу в строке
for char in input_string:
    # Если символ не пробел, добавляем его к текущему слову
    if char != ' ':
        current_word += char
    else:
        # Если слово не пустое и оканчивается на 'u', добавляем в список
        if current_word and current_word[-1] == 'u':
            words_with_u.append(current_word)
        current_word = ""  # Сбрасываем текущее слово

# Проверяем последнее слово в строке (после цикла)
if current_word and current_word[-1] == 'u':
    words_with_u.append(current_word)

# Выводим результат
print("Слова, оканчивающиеся на 'u':")
for word in words_with_u:
    print(word)