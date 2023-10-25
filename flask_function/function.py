from flask import Flask, request, jsonify
from database.Database import Database as db

app = Flask(__name__)

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

@app.route('/update_setting', methods=['POST'])
def webhook_update_setting():
    data = request.get_json()
    message_info = data['message_info']
    db().update_admin_settings_item(message_info)
    return jsonify(db().get_admin_settings_item_js(data['message_info']))

def start_flask_app():
    app.run(host='0.0.0.0')