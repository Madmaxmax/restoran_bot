from flask import Flask, request, jsonify
from database.Database import Database as db
from database.Settings_database import Settings_database

app = Flask(__name__)


@app.route('/messages')
def serve_html_messages():
    with open('edit_messages.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content


@app.route('/orders')
def serve_html_orders():
    with open('mobile_out.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content


@app.route('/view_couriers')
def serve_html_couriers():
    with open('mobile_view_couriers.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content


@app.route('/view_customers')
def serve_html_customers():
    with open('mobile_view_customers.html', 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content


@app.route('/get_messages', methods=['GET'])
def webhook_get_messages():
    return jsonify(Settings_database().get_all_messages())


@app.route('/update_message', methods=['POST'])
def webhook_update_message():
    message_type = request.form['message_type']
    message_text = request.form['message_text']
    print(message_type, message_text)
    Settings_database().update_message(message_type, message_text)
    return jsonify('good')


@app.route('/update_privilege', methods=['POST'])
def webhook_update_privilege():
    user_id = request.form['user_id']
    privilege_value = request.form['privilege_value']
    print(user_id, privilege_value)
    db().update_privilege(user_id, privilege_value)
    return jsonify('good')


@app.route('/stat', methods=['GET'])
def webhook_get_stat():
    return jsonify(db().get_all_orders_sort_data())


@app.route('/setting', methods=['GET'])
def webhook_get_settings():
    return jsonify(db().get_all_settings())


@app.route('/couriers', methods=['GET'])
def webhook_get_courier():
    return jsonify(db().get_all_courier())


@app.route('/customers', methods=['GET'])
def webhook_get_customers():
    return jsonify(db().get_all_customers())


def start_flask_app():
    app.run(host='0.0.0.0')
