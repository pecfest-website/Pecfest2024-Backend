from flask import request
from util.loggerSetup import logger
from util.exception import PecfestException

def tokenChecker(token):
    return True

def general(logReq = False, checkToken = False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            headers = request.headers
            body = request.json
            if logReq:
                headers_str = ', '.join(f"{key}: {value}" for key, value in headers.items())
                logger.info(f"Request: {request.method} {request.url} | Headers: {headers_str} | Body: {body}")

            if checkToken:
                if not headers.get("token"):
                    raise PecfestException(statusCode=404, message="Please provide token")
                if not tokenChecker(headers['token']):
                    raise PecfestException(statusCode=401, message="Session expired, login agian!")

            output = func(body, *args, **kwargs)
            return output
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator