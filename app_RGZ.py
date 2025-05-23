from flask import Flask, jsonify, request

app = Flask(__name__)

# Статические курсы валют (можно изменить)
STATIC_RATES = {
    "USD": 79.71,
    "EUR": 90.52
}

@app.route('/rate', methods=['GET'])
def get_rate():
    try:
        currency = request.args.get('currency', '').upper()

        # Проверка корректности валюты
        if currency not in STATIC_RATES:
            return jsonify({"message": "UNKNOWN CURRENCY"}), 400

        # Возврат курса
        return jsonify({"rate": STATIC_RATES[currency]}), 200

    except Exception as e:
        # Обработка внутренних ошибок
        return jsonify({"message": "UNEXPECTED ERROR"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)