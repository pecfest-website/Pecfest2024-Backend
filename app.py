from flask import Flask, jsonify, request
from tables import User, DBConnectionManager
from flask_cors import CORS
from controllers import user
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

# ----------------------- EVENT Routes --------------------------

# ------------------------ USER Routes ----------------------------
@app.route('/users/create', methods=['POST'])
@general(logReq = True, checkToken = True)
def create_user(body, *args, **kwargs):
    result = user.createUser(body)
    return result, 201

if __name__ == '__main__':
    app.run(debug=True)
