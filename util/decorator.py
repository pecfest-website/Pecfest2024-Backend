from flask import request
from util.loggerSetup import logger
from util.exception import PecfestException
import redis
import json

redisClient = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def tokenChecker(token):
    try:
        token = token.split(" ")[1]
        user = redisClient.get(token)

        return json.loads(user)
    except Exception as e:
        logger.error(f"invalid token , {e}")
        raise PecfestException(statusCode=403, message="Invalid token provided")

def general(logReq=False, checkToken=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            headers = request.headers
            user = None
            # Log request details
            if logReq:
                headers_str = ', '.join(f"{key}: {value}" for key, value in headers.items())
                body = request.get_json() if request.method != 'GET' else None
                logger.info(f"Request: {request.method} {request.url} | Headers: {headers_str} | Body: {body}")

            # Check token if required
            if checkToken:
                token = headers.get("token")
                if not token:
                    logger.error("Token missing in request")
                    raise PecfestException(statusCode=404, message="Please provide token")
                
                user = tokenChecker(token)
                if not user:
                    logger.error("Token validation failed")
                    raise PecfestException(statusCode=401, message="Session expired, login again!")


            # Call the original function depending on the request method
            if request.method == 'GET':
                # For GET requests, we don't pass the body
                return func(*args, **kwargs)
            else:
                # For POST, PUT, etc. requests, pass the JSON body
                body = request.json
                body['reqUser'] = user if user else None
            output = func(body, *args, **kwargs)
            return output
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator