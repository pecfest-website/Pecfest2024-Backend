from tables import DBConnectionManager, User
from util.exception import PecfestException
from util.loggerSetup import logger

def createUser(body):
    with DBConnectionManager() as session:  

        if not body.get('name'):
            raise PecfestException(statusCode=301, message="Please provide name")
        try:
            newUser = User(name = body["name"])
            session.add(newUser)
            session.commit()
        except Exception as e:
            logger.error(f"Err occured in createUser: {e.traceback()}")
            raise PecfestException()

    return {"status": "SUCCESS", "statusCode": 200, "message": "User created successfully"}