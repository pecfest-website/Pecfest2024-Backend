from tables import DBConnectionManager, Admin, Event, User, Tag, Head
from util.exception import PecfestException
from util.loggerSetup import logger
from flask import make_response, jsonify
from controllers.user import generateToken
from controllers.event import listEvent
import redis
import json

redisClient = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def login(body):
    if not body.get('username'):
        raise PecfestException(statusCode=301, message="Please provide username")
    if not body.get('password'):
        raise PecfestException(statusCode=301, message="Please provide password")
    
    username, password = body['username'], body['password']

    with DBConnectionManager() as session:
        admin = session.query(Admin).filter(Admin.username==body["username"]).first()
        
        if not admin:
            raise PecfestException(statusCode=404, message="Admin not found")
        
        if admin.password != password:
            raise PecfestException(statusCode=401, message="Invalid password")

        token = generateToken(admin.password)
        redisClient.set(token, json.dumps(admin.to_dict()))  # Assuming `redisClient` is available

        return {
            "status": "SUCCESS",
            "statusCode": 200,
            "message": "Admin logged in successfully",
            "data": {"token": token}
        }

def listEvents(body):
    body = {
        "filters": {
            "adminId": body.get('reqUser').get("id") if body.get("reqUser") else None
        }
    }
    print(body)
    return listEvent(body)

def addEvent(body):
    body['adminId'] = body.get("reqUser").get("id") if body.get("reqUser") else None
    with DBConnectionManager() as session:
        required_fields = [
            'name', 'description', 'startdate', 'starttime', 'enddate', 'endtime',
            'venue', 'eventtype', 'minparticipants', 'maxparticipants', 'registrationfee',
            'heads', 'tags', 'participationType', 'paymentType', 'ruleBookType', 'adminId'
        ]
        
        for field in required_fields:
            if not body.get(field):
                logger.debug(f"Missing required field: {field}")
                raise PecfestException(statusCode=301, message=f"Please provide {field}")

        heads = [Head(name=head["name"], phoneNumber=head["contact"]) for head in body["heads"]]
        
        try:
            logger.debug("Creating new event with provided details.")
            new_event = Event(
                name=body["name"],
                description=body["description"],
                startDate=body["startdate"],
                startTime=body["starttime"],
                endDate=body["enddate"],
                endTime=body["endtime"],
                venue=body["venue"],
                eventType=body["eventtype"],
                minParticipants=body["minparticipants"],
                maxParticipants=body["maxparticipants"],
                registrationFee=body["registrationfee"],
                ruleBookLink=body.get("rulebooklink"),
                heads=heads,  
                tags=body["tags"],    
                image=body.get("image"),
                participationType=body["participationType"],
                paymentType=body["paymentType"],
                ruleBookType=body["ruleBookType"],
                adminId=body["adminId"]
            )
            logger.debug(f"New event created: {new_event}")
            session.add(new_event)
            session.commit()
            logger.debug("Event added to the database successfully.")
            return {"status": "SUCCESS", "responseCode": 200, "message": "Event added successfully"}
        except Exception as e:
            logger.error(f"Error occurred in add_event: {e}")
            raise PecfestException(statusCode=500, message="Internal server error")
        
def eventDetail(body):
    with DBConnectionManager() as session:
        try:
            query = session.query(Event)
            
            if 'event_id' in body:
                query = query.filter(Event.id == body['event_id'])
            if 'event_name' in body:
                query = query.filter(Event.name == body['event_name'])
            
            students = query.all()
            student_list = [
                {
                    "name": student.name,
                    "contact_number": student.contact_number,
                    "email": student.email
                } for student in students
            ]
            return {"status": "SUCCESS", "responseCode": 200, "message": "Students retrieved successfully", "data": student_list}
        except Exception as e:
            logger.error(f"Err occurred in event_detail: {e}")
            raise PecfestException(statusCode=500, message="Internal server error")

def listTag():
    with DBConnectionManager() as session:
        tags = session.query(Tag).all()
        return {
            "status": "SUCCESS",
            "statusCode": 200,
            "message": "Tags fetched successfully",
            "data": {
                "tags": tags
            }
        }