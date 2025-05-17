import random
from flask import Flask, request, jsonify

# Создаём Flask-приложение
app = Flask(__name__)

# эндпоинт для GET-запроса /number/
@app.route('/number/', methods=['GET'])
def get_number():
    param = request.args.get('param', type=int) #получаем параметр из URL

    if param is None:
        return jsonify({'error': 'Необходим параметр param'}), 400

    random_run = random.uniform(0, 100) # геренируем случайное число
    result = random_run * param # умножение на параметр param

    return jsonify({'result': result})


# POST эндпоинт /number/
@app.route('/number/', methods=['POST'])
def post_number():
    data = request.get_json()  # Получаем JSON из тела запроса

    # Проверяем, есть ли поле 'jsonParam'
    if not data or 'jsonParam' not in data:
        return jsonify({'error': 'Необходимо поле jsonParam'}), 400

    json_param = data['jsonParam']  # Получаем значение из JSON
    random_num = random.uniform(0, 100)  # Генерируем случайное число

    # Выбираем случайную операцию
    operation = random.choice(['+', '-', '*', '/'])

    # Вычисляем результат в зависимости от операции
    if operation == '+':
        result = random_num + json_param
    elif operation == '-':
        result = random_num - json_param
    elif operation == '*':
        result = random_num * json_param
    elif operation == '/':
        # Проверяем деление на ноль
        result = random_num / json_param if json_param != 0 else 'Ошибка: деление на ноль'

    # Возвращаем результат в JSON
    return jsonify({
        'random_number': random_num,
        'operation': operation,
        'result': result
    })

# Эндпоинт для DELETE-запроса
@app.route('/number/', methods=['DELETE'])
def delete_number():
    random_num = random.uniform(0, 100)  # Генерируем случайное число
    operation = random.choice(['+', '-', '*', '/'])  # Выбираем случайную операцию

    return jsonify({
        'random_number': random_num,
        'operation': operation
    })

# Запускаем сервер
if __name__ == '__main__':
    app.run(debug=True)