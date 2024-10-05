from tables import DBConnectionManager, Admin, Event, User, Tag
from util.exception import PecfestException
from util.loggerSetup import logger
from flask import make_response, jsonify
from controllers.user import generateToken
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
    admin_id = body.get("admin_id")
    with DBConnectionManager() as session:
        try:
            logger.debug("Opening DB session")
            logger.debug("Querying all events created by the admin from the database.")
            events = session.query(Event).filter(Event.adminId == admin_id).all()
            logger.debug(f"Number of events retrieved: {len(events)}")
            
            event_list = []
            for event in events:
                logger.debug(f"Processing event: {event.name}")
                event_list.append({
                    "name": event.name,
                    "description": event.description,
                    "startdate": event.startdate.strftime("%Y-%m-%d") if event.startdate else None,
                    "starttime": event.starttime,
                    "enddate": event.enddate.strftime("%Y-%m-%d") if event.enddate else None,
                    "endtime": event.endtime,
                    "venue": event.venue,
                    "eventtype": event.eventtype,
                    "minparticipants": event.minparticipants,
                    "maxparticipants": event.maxparticipants,
                    "registrationfee": event.registrationfee,
                    "rulebooklink": event.rulebooklink,
                    "tags": event.tags,
                    "image": event.image,
                    "participationType": event.participationType,
                    "paymentType": event.paymentType,
                    "ruleBookType": event.ruleBookType,
                    "created_at": event.createdAt.strftime("%Y-%m-%d %H:%M:%S") if event.createdAt else None,
                    "updated_at": event.updatedAt.strftime("%Y-%m-%d %H:%M:%S") if event.updatedAt else None,
                })
            
            logger.debug(f"Event list created: {event_list}")
            return {"status": "SUCCESS", "responseCode": 200, "message": "Events retrieved successfully", "data": event_list}
        except Exception as e:
            logger.error(f"Error occurred in list_admins: {e}")
            raise PecfestException(statusCode=401, message="Invalid credentials")

def addEvent(body):
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
        
        try:
            logger.debug("Creating new event with provided details.")
            new_event = Event(
                name=body["name"],
                description=body["description"],
                startdate=body["startdate"],
                starttime=body["starttime"],
                enddate=body["enddate"],
                endtime=body["endtime"],
                venue=body["venue"],
                eventtype=body["eventtype"],
                minparticipants=body["minparticipants"],
                maxparticipants=body["maxparticipants"],
                registrationfee=body["registrationfee"],
                rulebooklink=body.get("rulebooklink"),
                heads=body["heads"],  
                tags=body["tags"],    
                image=body.get("image"),
                participationType=body["participationType"],
                paymentType=body["paymentTime"],
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