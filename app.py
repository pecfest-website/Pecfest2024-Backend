from flask import Flask, jsonify, request
from flask_cors import CORS
from controllers import user
from controllers import admin, user, sponser
from util.decorator import general
from util.exception import PecfestException
from util.loggerSetup import logger
from dotenv import load_dotenv
from util.loggerSetup import logger
from util.gcb import uploadToGcs

load_dotenv()
app = Flask(__name__)
CORS(app)

@app.errorhandler(Exception)
def handle_global_exception(error):
    if isinstance(error, PecfestException):
        return jsonify(error.to_dict()), 200

    logger.error(f"Err: Global Error - {error}")
    
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

@app.route('/admin/event/list', methods=['POST'])
@general(logReq=True, checkToken=True)
def list_admins(*args, **kwargs):
    admin_id = request.cookies.get('admin_id')
    result = admin.list_admins(admin_id)
    return result, 200
    
@app.route('/admin/event/add', methods=['POST'])
@general(logReq = True, checkToken=True)
def add_event(body, *args, **kwargs):
    result = admin.add_event(body)
    return result, 200

@app.route('/admin/event/detail', methods=['POST'])
@general(logReq = True, checkToken=True)
def event_detail(body, *args, **kwargs):
    result = admin.event_detail(body)
    return result, 200

# ----------------------- EVENT Routes --------------------------

# ---------------------- Sponsper Routes ------------------------
@app.route('/admin/sponserType/create', methods=['POST'])
@general(logReq=True, checkToken=True)
def createSponserType(body, *args, **kwargs):
    result = sponser.addType(body)
    return result, 201

@app.route('/admin/sponser/add', methods=['PATCH']) 
@general(logReq=True, checkToken=True)
def addSponser(body, *args, **kwargs):
    result = sponser.addSponser(body)
    return result, 200

# ------------------------ USER Routes ----------------------------
@app.route('/users/create', methods=['GET'])
@general(logReq = True, checkToken = True)
def create_user(body, *args, **kwargs):
    blob = "hellp"
    print("hello")
    try:
        result = uploadToGcs(blob, "test")
    except Exception as e:
        print(e)

    print("hello")
    return result, 201

if __name__ == '__main__':
    app.run(debug=True)
