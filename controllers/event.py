from tables import Event, DBConnectionManager, Team, User
from sqlalchemy.orm import joinedload, noload
from util.exception import PecfestException
from flask import jsonify

def listEvent(body):
    filters = body.get("filters")
    with DBConnectionManager() as session:
        applyFilters = [True]
        if filters:
            if filters.get("eventType"):
                applyFilters.append(Event.eventType==filters.get("eventType"))
            
            if filters.get("adminId"):
                applyFilters.append(Event.adminId==int(filters.get("adminId")))

        events = session.query(Event).filter(*applyFilters).options(noload("*")).all()

        for event in events:
            event.startDate = event.startDate.strftime("%Y-%m-%d") if event.startDate else None
            event.startTime = event.startTime.strftime("%H:%M:%S") if event.startTime else None
            event.endDate = event.endDate.strftime("%Y-%m-%d") if event.endDate else None
            event.endTime = event.endTime.strftime("%H:%M:%S") if event.endTime else None
            event.eventType = event.eventType.name
            event.participationType = event.participationType.name
            event.paymentType = event.paymentType.name
        return {
            "statusCode": 200,
            "status": "SUCCESS",
            "message": "Events fetched successfully",
            "data": {
                "events": events
            }
        }

def eventDetails(body):
    eventId = body.get("eventId")
    if not eventId:
        raise PecfestException(statusCode=301, message="Please provide event id")

    filters = [True]
    if body.get("adminId"):
        filters.append(Event.adminId == int(body.get("adminId")))
    else:
        raise PecfestException(statusCode=403, message="You dont have authority to use this feature")

    with DBConnectionManager() as session:
        event = session.query(Event).filter(Event.id == eventId, *filters).options(joinedload(Event.participants), joinedload(Event.heads)).first()
        if not event:
            raise PecfestException(statusCode=404, message="No event exists")

        event.startDate = event.startDate.strftime("%Y-%m-%d") if event.startDate else None
        event.startTime = event.startTime.strftime("%H:%M:%S") if event.startTime else None
        event.endDate = event.endDate.strftime("%Y-%m-%d") if event.endDate else None
        event.endTime = event.endTime.strftime("%H:%M:%S") if event.endTime else None
        event.eventType = event.eventType.name
        event.participationType = event.participationType.name
        event.paymentType = event.paymentType.name

        participantIds = [participant.participantId for participant in event.participants]
        print(participantIds)
        participants = []
        if event.participationType == "TEAM":
            participants = session.query(Team).options(joinedload(Team.members)).filter(Team.id.in_(participantIds)).all()
            userIds = []
            for part in participants:
                for mem in part.members:
                    mem.memberType = mem.memberType.name
                    userIds.append(mem.userId)
            
            users = session.query(User).filter(User.id.in_(userIds)).all()
            users = {user.id: user for user in users}

            participants = jsonify(participants).json
            for part in participants:
                for mem in part["members"]:
                    mem["user"] = users.get(mem['userId'])
        else:
            participants = session.query(User).filter(User.id.in_(participantIds)).all()
    
        event = jsonify(event).json
        event['participants'] = participants

        return {
            "statusCode": 200,
            "status": "SUCCESS",
            "message": "Events fetched successfully",
            "data": {
                "event": event
            }
        }



        
