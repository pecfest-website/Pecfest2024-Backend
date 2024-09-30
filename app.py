from flask import Flask, jsonify, request
from tables import User, DBConnectionManager
from flask_cors import CORS
from controllers import user
from controllers import admin
from util.decorator import general
from util.exception import PecfestException
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

@app.errorhandler(Exception)
def handle_global_exception(error):
    if isinstance(error, PecfestException):
        return jsonify(error.to_dict()), 200
    
    # For all other exceptions, return a generic message
    return jsonify({
        "status": "FAILED",
        "statusCode": 500,
        "message": "An unexpected error occurred. Please try again later."
    }), 200

# ---------------------- ADMIN Routes --------------------------
@app.route('/admin/login', methods=['POST'])
@general(logReq = True, checkToken=False)
def login_admin(body, *args, **kwargs):
    result = admin.login(body)
    return result, 200

@app.route('/admin/list', methods=['GET'])
@general(logReq = True, checkToken=False)
def list_admins(*args, **kwargs):
    result = admin.list_admins()
    return result, 200

@app.route('/admin/add/event', methods=['POST'])
@general(logReq = True, checkToken=False)
def add_event(body, *args, **kwargs):
    result = admin.add_event(body)
    return result, 200

@app.route('/admin/event/detail', methods=['POST'])
@general(logReq = True, checkToken=False)
def event_detail(body, *args, **kwargs):
    result = admin.event_detail(body)
    return result, 200

# ----------------------- EVENT Routes --------------------------

# ------------------------ USER Routes ----------------------------
@app.route('/users/create', methods=['POST'])
@general(logReq = True, checkToken = True)
def create_user(body, *args, **kwargs):
    result = user.createUser(body)
    return result, 201

if __name__ == '__main__':
    app.run(debug=True)
