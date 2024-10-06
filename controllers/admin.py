from tables import DBConnectionManager, Admin, Event, User, Tag, Head
from util.exception import PecfestException
from util.loggerSetup import logger
from flask import make_response, jsonify
from controllers.user import generateToken
from controllers.event import listEvent, eventDetails
from util.gcb import uploadImage
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
            'heads', 'tags', 'participationType', 'paymentType', 'ruleBookType', 'adminId', 'image', 'provideAccommodation'
        ]
        
        for field in required_fields:
            if not body.get(field):
                logger.debug(f"Missing required field: {field}")
                raise PecfestException(statusCode=301, message=f"Please provide {field}")

        link = uploadImage(body['image'], body['eventtype'], "event")
        heads = [Head(name=head["name"], phoneNumber=head["contact"]) for head in body["heads"]]
        
        if (body["ruleBookType"] == 'true' and not body.get("rulebooklink")):
            raise PecfestException(statusCode=301, message="Please provide rule book link")
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
                participationType=body["participationType"],
                paymentType=body["paymentType"],
                haveRuleBook=body["ruleBookType"] == 'true',
                adminId=body["adminId"],
                image=link,
                provideAccommodation=body['provideAccommodation']
            )
            logger.debug(f"New event created: {new_event}")
            session.add(new_event)
            session.commit()
            logger.debug("Event added to the database successfully.")
            return {"status": "SUCCESS", "statusCode": 200, "message": "Event added successfully"}
        except Exception as e:
            logger.error(f"Error occurred in add_event: {e}")
            raise PecfestException(statusCode=500, message="Internal server error")

def eventDetail(body):
    body['adminId'] = body.get("reqUser").get("id") if body.get("reqUser") else None
    
    return eventDetails(body)

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