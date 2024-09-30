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
            if admin and admin.password == body["password"]:
                return {"status": "SUCCESS", "responseCode": 200, "message": "Login successful"}
            else:
                return {"status": "FAILURE", "responseCode": 401, "message": "Invalid credentials"}
        except Exception as e:
            logger.error(f"Err occurred in login: {e}")
            return {"status": "FAILURE", "responseCode": 500, "message": "Internal server error"}
        
def list_admins():
    with DBConnectionManager() as session:
        try:
            admins = session.query(Admin).all()
            admin_list = [
                {
                    "name": admin.username,
                    "date": admin.created_at.strftime("%Y-%m-%d"),
                    "time": admin.created_at.strftime("%H:%M:%S"),
                    "poster_link": admin.poster_link
                } for admin in admins
            ]
            return {"status": "SUCCESS", "responseCode": 200, "message": "Admins retrieved successfully", "data": admin_list}
        except Exception as e:
            logger.error(f"Err occurred in list_admins: {e}")
            return {"status": "FAILURE", "responseCode": 500, "message": "Internal server error"}
        
def add_event(body):
    with DBConnectionManager() as session:
        if not body.get('name'):
            return {"status": "FAILURE", "responseCode": 301, "message": "Please provide event name"}
        if not body.get('date'):
            return {"status": "FAILURE", "responseCode": 301, "message": "Please provide event date"}
        if not body.get('time'):
            return {"status": "FAILURE", "responseCode": 301, "message": "Please provide event time"}
        if not body.get('image'):
            return {"status": "FAILURE", "responseCode": 301, "message": "Please provide event image"}
        if not body.get('heads'):
            return {"status": "FAILURE", "responseCode": 301, "message": "Please provide event heads"}
        if not body.get('tags'):
            return {"status": "FAILURE", "responseCode": 301, "message": "Please provide event tags"}
        if not body.get('description'):
            return {"status": "FAILURE", "responseCode": 301, "message": "Please provide event description"}

        try:
            new_event = Event(
                name=body["name"],
                date=body["date"],
                time=body["time"],
                image=body["image"],
                heads=body["heads"],
                tags=body["tags"],
                description=body["description"]
            )
            session.add(new_event)
            session.commit()
            return {"status": "SUCCESS", "responseCode": 200, "message": "Event added successfully"}
        except Exception as e:
            logger.error(f"Err occurred in add_event: {e}")
            return {"status": "FAILURE", "responseCode": 500, "message": "Internal server error"}
        
def event_detail(body):
    with DBConnectionManager() as session:
        try:
            filters = body.get('filters', {})
            query = session.query(User).join(Event, User.event_id == Event.id)
            
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