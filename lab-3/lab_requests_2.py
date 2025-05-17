import requests
import random
from flask import Flask, request, jsonify

# Часть 1: Сервер (оставляем ваш исходный код)
app = Flask(__name__)


@app.route('/number/', methods=['GET'])
def get_number():
    param = request.args.get('param', type=float)
    if param is None:
        return jsonify({'error': 'Param required'}), 400
    random_num = random.uniform(0, 100)
    operation = random.choice(['+', '-', '*', '/'])
    return jsonify({
        'number': random_num,
        'operation': operation
    })


@app.route('/number/', methods=['POST'])
def post_number():
    data = request.get_json()
    if not data or 'jsonParam' not in data:
        return jsonify({'error': 'jsonParam required'}), 400
    random_num = random.uniform(0, 100)
    operation = random.choice(['+', '-', '*', '/'])
    return jsonify({
        'number': random_num,
        'operation': operation
    })


@app.route('/number/', methods=['DELETE'])
def delete_number():
    random_num = random.uniform(0, 100)
    operation = random.choice(['+', '-', '*', '/'])
    return jsonify({
        'number': random_num,
        'operation': operation
    })


# Часть 2: Клиент для отправки запросов
def calculate_expression():
    # 1. GET запрос
    get_num = random.randint(1, 10)
    get_response = requests.get(f'http://127.0.0.1:5000/number/?param={get_num}')
    get_data = get_response.json()
    print(f"GET: {get_data['number']} {get_data['operation']} {get_num}")

    # 2. POST запрос
    post_num = random.randint(1, 10)
    post_response = requests.post(
        'http://127.0.0.1:5000/number/',
        json={'jsonParam': post_num},
        headers={'Content-Type': 'application/json'}
    )
    post_data = post_response.json()
    print(f"POST: {post_data['number']} {post_data['operation']} {post_num}")

    # 3. DELETE запрос
    delete_response = requests.delete('http://127.0.0.1:5000/number/')
    delete_data = delete_response.json()
    print(f"DELETE: {delete_data['number']} {delete_data['operation']}")

    # 4. Вычисление выражения
    expression = f"{get_data['number']}{get_data['operation']}{get_num}{post_data['operation']}{post_num}{delete_data['operation']}{delete_data['number']}"
    result = eval(expression)  # Внимание: eval используйте только с доверенными данными!
    return int(result)


if __name__ == '__main__':
    # Запускаем сервер в отдельном потоке
    from threading import Thread

    Thread(target=lambda: app.run(debug=True, use_reloader=False)).start()

    # Даем серверу время запуститься
    import time

    time.sleep(1)

    # Вычисляем и выводим результат
    final_result = calculate_expression()
    print(f"\nФинальный результат (int): {final_result}")