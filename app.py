from flask import Flask, jsonify, request
from flask_cors import CORS
from controllers import admin, sponser, user, event
from util.decorator import general
from util.exception import PecfestException
from util.loggerSetup import logger
from dotenv import load_dotenv
from util.gcb import uploadToGcs
import traceback

load_dotenv()
app = Flask(__name__)
CORS(app)

@app.errorhandler(Exception)
def handle_global_exception(error):
    if isinstance(error, PecfestException):
        return jsonify(error.to_dict()), 200

    logger.error(f"Err: Global Error - {error}\nTraceback: {traceback.format_exc()}")
    
    # For all other exceptions, return a generic message
    return jsonify({
        "status": "FAILED",
        "statusCode": 500,
        "message": "An unexpected error occurred. Please try again later."
    }), 200

# ---------------------- ADMIN Routes --------------------------
@app.route('/admin/login', methods=['POST'])
@general(logReq = True, checkToken=False)
def loginAdmin(body, *args, **kwargs):
    result = admin.login(body)
    return result, 200

@app.route('/admin/event/list', methods=['POST'])
@general(logReq=True, checkToken=True)
def listAdminEvents(body, *args, **kwargs):
    result = admin.listEvents(body)
    return result, 200
    
@app.route('/admin/event/add', methods=['POST'])
@general(logReq = True, checkToken=True)
def addEvent(body, *args, **kwargs):
    result = admin.addEvent(body)
    return result, 200

@app.route('/admin/event/detail', methods=['POST'])
@general(logReq = True, checkToken=True)
def eventDetail(body, *args, **kwargs):
    result = admin.eventDetail(body)
    return result, 200

@app.route('/admin/tag/list', methods=['POST'])
@general(logReq=True, checkToken=False)
def listTag(body, *args, **kwargs):
    result = admin.listTag()
    return jsonify(result), 200

# ----------------------- EVENT Routes --------------------------
@app.route('/event/list', methods=['POST'])
@general(logReq=True, checkToken=False)
def listEvents(body, *args, **kwargs):
    result = event.listEvent(body)
    return jsonify(result), 200

@app.route('/event/register', methods=['POST'])
@general(logReq=True, checkToken=True)
def regEvent(body, *args, **kwargs):
    result = event.register(body)
    return jsonify(result), 200

@app.route('/event/detail', methods=['POST'])
@general(logReq=True, checkToken=False, tryUser=True)
def detailEvent(body, *args, **kwargs):
    result = event.eventDetail(body)
    return jsonify(result), 200

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

@app.route("/sponser/list", methods=['POST'])
@general(logReq=True, checkToken=False)
def listSponser(*args, **kwargs):
    result = sponser.listSponser()
    return jsonify(result), 200

@app.route("/admin/sponser/delete", methods=['POST'])
@general(logReq=True, checkToken=True)
def deleteType(body, *args, **kwargs):
    result = sponser.deleteType(body)
    return result, 200

# ------------------------ USER Routes ----------------------------
@app.route('/user/create', methods=['POST'])
@general(logReq = True, checkToken = False)
def createUser(body, *args, **kwargs):
    result = user.createUser(body)
    return result, 201

@app.route('/user/login', methods=['POST'])
@general(logReq = True, checkToken = False)
def loginUser(body, *args, **kwargs):
    result = user.loginUser(body)
    return result, 200

@app.route('/user/info', methods=['POST'])
@general(logReq = True, checkToken = True)
def InfoUser(body, *args, **kwargs):
    result = user.userInfo(body)
    return result, 200

if __name__ == '__main__':
    app.run(debug=True)
