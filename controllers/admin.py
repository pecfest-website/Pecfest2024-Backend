from tables import DBConnectionManager, Admin, Event, User
from util.exception import PecfestException
from util.loggerSetup import logger


def login(body):
    with DBConnectionManager() as session:
        if not body.get('username'):
            return {"status": "FAILURE", "responseCode": 301, "message": "Please provide username"}
        if not body.get('password'):
            return {"status": "FAILURE", "responseCode": 301, "message": "Please provide password"}
        
        try:
            admin = session.query(Admin).filter_by(username=body["username"]).first()
            if admin:
                logger.info(f"Admin found: {admin.username}")
                if admin.password == body["password"]:
                    return {"status": "SUCCESS", "responseCode": 200, "message": "Login successful"}
                else:
                    logger.info(f"Password mismatch: {admin.password} != {body['password']}")
                    return {"status": "FAILURE", "responseCode": 401, "message": "Invalid credentials"}
            else:
                logger.info(f"No admin found with username: {body['username']}")
                return {"status": "FAILURE", "responseCode": 401, "message": "Invalid credentials"}
        except Exception as e:
            logger.error(f"Err occurred in login: {e}")
            return {"status": "FAILURE", "responseCode": 500, "message": "Internal server error"}
        
def list_admins():
    with DBConnectionManager() as session:
        try:
            logger.debug("Opening DB session")
            with DBConnectionManager() as session:
                logger.debug("Session opened successfully.")
            logger.debug("Querying all admins from the database.")
            admins = session.query(Admin).all()
            logger.debug(f"Number of admins retrieved: {len(admins)}")
            
            admin_list = []
            for admin in admins:
                logger.debug(f"Processing admin: {admin.username}")
                admin_list.append({
                    "username": admin.username,
                    "created_at": admin.created_at.strftime("%Y-%m-%d %H:%M:%S") if admin.created_at else None,
                    "poster_link": admin.poster_link
                })
            
            logger.debug(f"Admin list created: {admin_list}")
            return {"status": "SUCCESS", "responseCode": 200, "message": "Admins retrieved successfully", "data": admin_list}
        except Exception as e:
            logger.error(f"Err occurred in list_admins: {e}")
            return {"status": "FAILURE", "responseCode": 500, "message": "Internal server error"}

def add_event(body):
    with DBConnectionManager() as session:
        required_fields = [
            'name', 'description', 'startdate', 'starttime', 'enddate', 'endtime',
            'venue', 'eventtype', 'minparticipants', 'maxparticipants', 'registrationfee',
            'heads', 'tags'
        ]
        
        for field in required_fields:
            if not body.get(field):
                logger.debug(f"Missing required field: {field}")
                return {"status": "FAILURE", "responseCode": 301, "message": f"Please provide {field}"}
        
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
                image=body.get("image")
            )
            logger.debug(f"New event created: {new_event}")
            session.add(new_event)
            session.commit()
            logger.debug("Event added to the database successfully.")
            return {"status": "SUCCESS", "responseCode": 200, "message": "Event added successfully"}
        except Exception as e:
            logger.error(f"Error occurred in add_event: {e}")
            return {"status": "FAILURE", "responseCode": 500, "message": "Internal server error"}
        
def event_detail(body):
    with DBConnectionManager() as session:
        try:
            filters = body.get('filters', {})
            # query = session.query(Event).join(Event, Event.event_id == Event.id)
            query = session.query(Event)
            
            if 'event_id' in filters:
                query = query.filter(Event.id == filters['event_id'])
            if 'event_name' in filters:
                query = query.filter(Event.name == filters['event_name'])
            
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
            return {"status": "FAILURE", "responseCode": 500, "message": "Internal server error"}