from tables import Event, DBConnectionManager, Team, User, ParticipationTypeEnum, PaymentTypeEnum, Participant, Team, TeamMember, MemberTypeEnum, Tag
from sqlalchemy.orm import joinedload, noload
from util.exception import PecfestException
from flask import jsonify
from util.gcb import uploadImage

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
        tags = session.query(Tag).all()
        tags = {int(tag.id): tag.name for tag in tags}

        for event in events:
            event.startDate = event.startDate.strftime("%Y-%m-%d") if event.startDate else None
            event.startTime = event.startTime.strftime("%H:%M:%S") if event.startTime else None
            event.endDate = event.endDate.strftime("%Y-%m-%d") if event.endDate else None
            event.endTime = event.endTime.strftime("%H:%M:%S") if event.endTime else None
            event.eventType = event.eventType.name
            event.participationType = event.participationType.name
            event.paymentType = event.paymentType.name
            event.tagNames = [tags.get(int(tag)) for tag in event.tags]
            
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

        participants = []
        if event.participationType == "TEAM":
            participants = session.query(Team).options(joinedload(Team.members).joinedload(TeamMember.user)).filter(Team.id.in_(participantIds)).all()

            for part in participants:
                for mem in part.members:
                    mem.memberType = mem.memberType.name

        else:
            participants = session.query(User).filter(User.uuid.in_(participantIds)).all()
    
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



        
def register(body):
    user = body['reqUser']
    userId = user.get("userId")
    eventId = body.get('eventId')
    accomo = body.get("accomodation")

    if not userId:
        raise PecfestException(statusCode=403, message="Invalid User")

    if not eventId:
        raise PecfestException(statusCode=301, message="Please provide event id")

    if not accomo:
        raise PecfestException(statusCode=301, message="Please provide accomodation field")

    with DBConnectionManager() as session:
        event = session.query(Event).filter(Event.id == eventId).first()
        if not event:
            raise PecfestException(statusCode=404, message="No such event exists")

        participant = Participant(eventId=eventId, requireAccomodations=accomo)
        if event.participationType == ParticipationTypeEnum.SINGLE:
            participant.participantId = userId
        else:
            teamName = body.get("teamName")
            teamSize = body.get('teamSize')
            members = body.get("members")

            if not teamName:
                raise PecfestException(statusCode=301, message="Please provide team name")

            if not teamSize:
                raise PecfestException(statusCode=301, message="Please provide team size")

            if not members:
                raise PecfestException(statusCode=301, message="Please provide team members")

            teamMem = [TeamMember(userId=mem, memberType=MemberTypeEnum.INVITED) for mem in members]
            teamMem.append(TeamMember(userId=user.uuid, memberType=MemberTypeEnum.ACCEPTED))
            team = Team(teamName=teamName, teamSize=teamSize, members=teamMem)

            session.add(team)
            session.commit()
            participant.participantId = team.id

        if event.paymentType == PaymentTypeEnum.PAID:
            paymentId = body.get("paymentId")
            billAddress = body.get("billAddress")
            paymentProof = body.get("paymentProof")

            if not paymentId:
                raise PecfestException(statusCode=301, message="Please provide payment Id")

            if not billAddress:
                raise PecfestException(statusCode=301, message="Please provide billing address")

            if not paymentProof:
                raise PecfestException(statusCode=301,message="Please provide payment proof")

            link = uploadImage(paymentProof, "proof", event.eventType.name)

            participant.billingAddress = billAddress
            participant.paymentId = paymentId
            participant.paymentProof = link

        session.add(participant)
        session.commit()

        return {
            "status": "SUCCESS",
            "statusCode": 200,
            "message": "Registered successfully"
        }
