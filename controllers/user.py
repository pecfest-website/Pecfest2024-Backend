from tables import DBConnectionManager, User
from util.exception import PecfestException
from util.loggerSetup import logger
from flask import jsonify
import datetime
import redis
import secrets
import string
import jwt
import os
import bcrypt
import json

JWT=os.getenv("JWT")
redisClient = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def generateUniqueUserId():
    with DBConnectionManager() as session:
        existingIds = session.query(User.uuid).all()
        characters = string.ascii_uppercase + string.digits  
        while True:
            uniqueId = ''.join(secrets.choice(characters) for _ in range(6))  
            if uniqueId not in existingIds: 
                return uniqueId

def generateToken(userUuid):
    token = jwt.encode({
                'userUuid': userUuid,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)  # Token valid for 1 day
            }, JWT, algorithm='HS256')
    return token 

def createUser(body):
    with DBConnectionManager() as session:  
        
        # Check for required fields
        if not body.get('name'):
            raise PecfestException(statusCode=301, message="Please provide name")
        
        if not body.get('college'):
            raise PecfestException(statusCode=301, message="Please provide college name")

        if not body.get('sid'):
            raise PecfestException(statusCode=301, message="Please provide student ID")

        if not body.get('email'):
            raise PecfestException(statusCode=301, message="Please provide email")

        if not body.get('contact'):
            raise PecfestException(statusCode=301, message="Please provide contact number")

        if not body.get("password"):
            raise PecfestException(statusCode=301, message="Please provide password")

        body['password'] = bcrypt.hashpw(body["password"].encode('utf-8'), bcrypt.gensalt())

        # Generate UUID for the new user
        userUuid = generateUniqueUserId()

        # Create a new User object
        newUser = User(
            name=body["name"],
            college=body["college"],
            sid=body["sid"],
            email=body["email"],
            contact=body["contact"],
            password=body['password'],
            uuid=userUuid
        )

        try:
            session.add(newUser)
            session.commit()


        except Exception as e:
            session.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise PecfestException(statusCode=500, message="Failed to create user")


        token = generateToken(newUser.uuid)
        redisClient.set(token, json.dumps(newUser.to_dict()))
    return {"status": "SUCCESS",
        "statusCode": 200,
        "message": "User created successfully",
        "data": {
            "token": token
        }
    }

def loginUser(body):

    if not body.get("email"):
        raise PecfestException(statusCode=301, message="Please provide email id")
    
    if not body.get("password"):
        raise PecfestException(statusCode=301, message="Please provide password")

    email, password = body['email'], body['password']

    with DBConnectionManager() as session:
        user = session.query(User).filter(User.email==email).first()
        
        if not user:
            raise PecfestException(statusCode=404, message="User not found")
        
        if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            raise PecfestException(statusCode=401, message="Invalid password")

        # Generate a token and save it in Redis
        token = generateToken(user.uuid)
        redisClient.set(token, json.dumps(user.to_dict()))

        return {
            "status": "SUCCESS",
            "statusCode": 200,
            "message": "User logged in successfully",
            "data": {
                "token": token
            }
        }