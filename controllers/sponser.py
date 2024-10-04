from tables import SponserType, Sponser
from util.exception import PecfestException
from util.loggerSetup import logger
from util.gcb import uploadToGcs

def addType(body):
    name = body.get("name")
    if not name:
        raise PecfestException(statusCode=301, message="Provide category name")

    try:
        sponserType = SponserType(name=name)
        session.add(sponserType)
        session.commit()

        images = body.get("photos")
        for image in images:
            print(image.filename)
            link = uploadToGcs(image,"/sponser/{name}/{image.filename}")
            sponser = Sponser(link= link,typeId=sponserType.id)
            session.add(sponser)
        session.commit()
    except Exception as e:
        logger.info(f"Err: Add Sponser type {e}")
        raise PecfestException()

    return {"status": "Success", "statusCode":200, "message": "Event type added successfully"}