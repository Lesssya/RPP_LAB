import random
import subprocess
import json
import time
from threading import Thread
from flask import Flask, jsonify

app = Flask(__name__)

# 1. Flask сервер (аналогичный предыдущему)
@app.route('/number/', methods=['GET'])
def get_number():
    param = request.args.get('param', type=float)
    if param is None:
        return jsonify({'error': 'Param required'}), 400
    return jsonify({
        'number': random.uniform(0, 100),
        'operation': random.choice(['+', '-', '*', '/'])
    })

# 2. Функция для выполнения curl-запросов
def run_curl(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return json.loads(result.stdout)

# 3. Вычисление выражения через curl
def calculate_with_curl():
    # GET запрос
    get_num = random.randint(1, 10)
    get_data = run_curl(f"curl -s 'http://127.0.0.1:5000/number/?param={get_num}'")
    print(f"GET: {get_data['number']} {get_data['operation']} {get_num}")

    # POST запрос
    post_num = random.randint(1, 10)
    post_data = run_curl(
        f"curl -s -X POST -H 'Content-Type: application/json' "
        f"-d '{{\"jsonParam\": {post_num}}}' http://127.0.0.1:5000/number/"
    )
    print(f"POST: {post_data['number']} {post_data['operation']} {post_num}")

    # DELETE запрос
    delete_data = run_curl("curl -s -X DELETE http://127.0.0.1:5000/number/")
    print(f"DELETE: {delete_data['number']} {delete_data['operation']}")

    # Вычисление
    expr = f"{get_data['number']}{get_data['operation']}{get_num}{post_data['operation']}{post_num}{delete_data['operation']}{delete_data['number']}"
    return int(eval(expr))

if __name__ == '__main__':
    # Запуск сервера в потоке
    Thread(target=lambda: app.run(port=5000)).start()
    time.sleep(1)

    # Вызов curl-клиента
    result = calculate_with_curl()
    print(f"\nРезультат (curl): {result}")