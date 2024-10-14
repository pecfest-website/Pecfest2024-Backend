from tables import Event, DBConnectionManager, Team, User, ParticipationTypeEnum, PaymentTypeEnum, Participant, Team, TeamMember, MemberTypeEnum, Tag
from sqlalchemy.orm import joinedload, noload, with_loader_criteria
from util.exception import PecfestException
from flask import jsonify
from util.gcb import uploadImage

def formatEvent(event, tags):
    event.startDate = event.startDate.strftime("%Y-%m-%d") if event.startDate else None
    event.startTime = event.startTime.strftime("%H:%M") if event.startTime else None
    event.endDate = event.endDate.strftime("%Y-%m-%d") if event.endDate else None
    event.endTime = event.endTime.strftime("%H:%M") if event.endTime else None
    event.eventType = event.eventType.name
    event.participationType = event.participationType.name
    event.paymentType = event.paymentType.name
    event.tags = [tags.get(int(tag)) for tag in event.tags]

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
            formatEvent(event, tags)
            
        return {
            "statusCode": 200,
            "status": "SUCCESS",
            "message": "Events fetched successfully",
            "data": {
                "events": events
            }
        }


def getParticipants(session, event):
    participantIds = []
    idToPart = {}
    for participant in event.participants:
        participantIds.append(participant.participantId)
        idToPart[participant.participantId] = participant

    participants = []

    if event.participationType == ParticipationTypeEnum.TEAM.name:
        teams = session.query(Team).options(joinedload(Team.members).joinedload(TeamMember.user), with_loader_criteria(TeamMember, TeamMember.memberType == MemberTypeEnum.ACCEPTED)).filter(Team.id.in_(participantIds)).all()
        for part in teams: 
            for mem in part.members:
                mem.memberType = mem.memberType.name
            participant = idToPart[str(part.id)]
            tmp = jsonify(part).json
            tmp['requireAccomodations'] = participant.requireAccomodations
            tmp['paymentId'] = participant.paymentId
            participants.append(tmp)

    else:
        users = session.query(User).filter(User.uuid.in_(participantIds)).all()
        for user in users:
            participant = idToPart[user.uuid]
            tmp = jsonify(user).json
            tmp['requireAccomodations'] = participant.requireAccomodations
            tmp['paymentId'] = participant.paymentId
            participants.append(tmp)
    
    return participants

def adminEventDetails(body):
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
        
        tags = session.query(Tag).all()
        tags = {int(tag.id): tag.name for tag in tags}

        formatEvent(event, tags)
        participants = getParticipants(session, event)

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

def eventDetail(body):
    eventId = body.get("eventId")
    if not eventId:
        raise PecfestException(statusCode=301, message="Please provide event id")

    with DBConnectionManager() as session:
        event = session.query(Event).filter(Event.id == eventId).options(joinedload(Event.heads), noload("*")).first()

        if not event:
            raise PecfestException(statusCode=404, message="No such event exists")

        tags = session.query(Tag).all()
        tags = {int(tag.id): tag.name for tag in tags}

        formatEvent(event, tags)

        event = jsonify(event).json
        event['participated'] = False

        if body.get("reqUser") and body.get("reqUser").get("userId"):
            userId = body.get("reqUser").get("userId")
            participants = session.query(Participant.participantId).filter(Participant.eventId == eventId).all()
            if Event.eventType == EventTypeEnum.Team.name:
                teams = session.query(Team).filter(Team.id.in_(participants)).all()
                joined = session.query(TeamMember).filter(TeamMember.teamId.in_(teams), TeamMember.memberType == MemberTypeEnum.ACCEPTED, TeamMember.userId == userId).first()
                if joined:
                    event['participated'] = True
            else:
                if userId in participants:
                    event['participated'] = True

        return {
            "status": "SUCCESS",
            "statusCode": 200,
            "message": "Details fetched successfully",
            "data": event
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

            if teamSize >= event.minParticipants and teamSize <= event.maxParticipants:
                raise PecfestException(statusCode=301, message=f"Please provide team size betwenn {event.minParticipants} and {event.maxParticipants}")

            if len(members) != (int(teamSize) - 1):
                raise PecfestException(statusCode=400, message=f"Please provide members equal to {teamSize -1}")

            if not members:
                raise PecfestException(statusCode=301, message="Please provide team members")

            teamMem = [TeamMember(userId=mem, memberType=MemberTypeEnum.INVITED) for mem in members]
            teamMem.append(TeamMember(userId=user.get("uuid"), memberType=MemberTypeEnum.ACCEPTED))
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
