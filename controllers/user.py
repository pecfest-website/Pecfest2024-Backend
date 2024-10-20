from tables import DBConnectionManager, User, TeamMember, Team, Participant
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

        if not body.get('username'):
            raise PecfestException(statusCode=301, message="Please provide username")
        
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

        userUuid = body['username'].strip()

        check = session.query(User).filter(User.uuid == userUuid).first()
        if check:
            raise PecfestException(statusCode=403, message=f"Username {userUuid} is already taken")

        check = session.query(User).filter(User.email == body['email']).first()
        if check:
            raise PecfestException(statusCode=403, message=f"Email {body['email']} is already used")

        check = session.query(User).filter(User.contact == body['contact']).first()
        if check:
            raise PecfestException(statusCode=403, message=f"Contact {body['contact']} is already used")

        body['password'] = bcrypt.hashpw(body["password"].encode('utf-8'), bcrypt.gensalt())

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

    if not body.get("username"):
        raise PecfestException(statusCode=301, message="Please provide username")
    
    if not body.get("password"):
        raise PecfestException(statusCode=301, message="Please provide password")

    username, password = body['username'].strip(), body['password']

    with DBConnectionManager() as session:
        user = session.query(User).filter(User.uuid==username).first()
        
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

def userInfo(body):
    reqUser = body.get("reqUser")

    if not reqUser:
        raise PecfestException(statusCode=400, message="Invalid Request")

    uuid = reqUser.get("uuid")

    with DBConnectionManager() as session:
        # Fetch the user by uuid
        user = session.query(User).filter(User.uuid == uuid).first()

        if not user:
            raise PecfestException(statusCode=401, message="Invalid user")

        # Fetch all teams the user is invited to with event information in one query
        invitedTeams = session.query(Team, Event).join(TeamMember).join(Event).filter(
            TeamMember.userId == uuid,
            TeamMember.memberType == MemberTypeEnum.INVITED
        ).all()

        # Fetch all teams where the user is an accepted member with event information in one query
        acceptedTeams = session.query(Team, Event).join(TeamMember).join(Event).filter(
            TeamMember.userId == uuid,
            TeamMember.memberType == MemberTypeEnum.ACCEPTED
        ).all()

        # Combine team IDs from both invited and accepted teams
        allTeamIds = list(set([team.id for team, _ in invitedTeams] + [team.id for team, _ in acceptedTeams]))

        # Fetch accepted members for all teams in one query
        acceptedMembers = session.query(TeamMember, User).join(User).filter(
            TeamMember.teamId.in_(allTeamIds),
            TeamMember.memberType == MemberTypeEnum.ACCEPTED
        ).all()

        # Create a dictionary to store accepted members by team ID
        acceptedMembersByTeam = {}
        for teamMember, user in acceptedMembers:
            if teamMember.teamId not in acceptedMembersByTeam:
                acceptedMembersByTeam[teamMember.teamId] = []
            acceptedMembersByTeam[teamMember.teamId].append({
                "name": user.name,
                "email": user.email,
                "contact": user.contact
            })

        # Prepare invitedTeamsData
        invitedTeamsData = []
        for team, event in invitedTeams:
            invitedTeamsData.append({
                "teamName": team.teamName,
                "eventName": event.name,
                "eventId": event.id,
                "eventType": event.participationType.name,  # Event Type (Single or Team)
                "teamSize": team.teamSize,
                "teamId": team.id,
                "acceptedMembers": acceptedMembersByTeam.get(team.id, []),
                "startTime": event.startTime,
                "startDate": event.startDate,
                "endTime": event.endTime,
                "endDate": event.endDate
            })

        # Prepare acceptedAndParticipantEvents (combining accepted teams and participant events)
        acceptedAndParticipantEvents = []
        
        # Process accepted teams
        for team, event in acceptedTeams:
            acceptedAndParticipantEvents.append({
                "teamName": team.teamName,
                "eventName": event.name,
                "eventId": event.id,
                "eventType": event.participationType.name,  # Event Type (Single or Team)
                "teamSize": team.teamSize,
                "teamId": team.id,
                "acceptedMembers": acceptedMembersByTeam.get(team.id, []),
                "startTime": event.startTime,
                "startDate": event.startDate,
                "endTime": event.endTime,
                "endDate": event.endDate
            })

        # Find all events the user is part of (as a participant) in one query
        participantEvents = session.query(Event).join(Participant).filter(
            Participant.participantId == uuid
        ).all()

        # Add participant events (individual participation) to acceptedAndParticipantEvents
        for event in participantEvents:
            acceptedAndParticipantEvents.append({
                "eventName": event.name,
                "eventId": event.id,
                "eventType": event.participationType.name,  # Event Type (Single or Team)
                "startTime": event.startTime,
                "startDate": event.startDate,
                "endTime": event.endTime,
                "endDate": event.endDate
            })

        # Prepare response data
        data = {
            "user": user.to_dict(),
            "invitedTeams": invitedTeamsData,
            "acceptedAndParticipantEvents": acceptedAndParticipantEvents
        }

        return {
            "status": "SUCCESS",
            "statusCode": 200,
            "message": "User info fetched successfully",
            "data": data
        }