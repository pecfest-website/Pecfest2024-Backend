from flask import request
from util.loggerSetup import logger
from util.exception import PecfestException

def tokenChecker(token):
    return True

def general(logReq=False, checkToken=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            headers = request.headers
            
            # Log request details
            if logReq:
                headers_str = ', '.join(f"{key}: {value}" for key, value in headers.items())
                body = request.json if request.method != 'GET' else None
                logger.info(f"Request: {request.method} {request.url} | Headers: {headers_str} | Body: {body}")

            # Check token if required
            if checkToken:
                token = headers.get("token")
                if not token:
                    logger.error("Token missing in request")
                    raise PecfestException(statusCode=404, message="Please provide token")
                if not tokenChecker(token):
                    logger.error("Token validation failed")
                    raise PecfestException(statusCode=401, message="Session expired, login again!")

            # Call the original function depending on the request method
            if request.method == 'GET':
                # For GET requests, we don't pass the body
                return func(*args, **kwargs)
            else:
                # For POST, PUT, etc. requests, pass the JSON body
                body = request.json
                return func(body, *args, **kwargs)
        
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator