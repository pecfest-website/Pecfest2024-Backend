from tables import SponserType, Sponser, DBConnectionManager
from util.exception import PecfestException
from util.loggerSetup import logger
from util.gcb import uploadToGcs

def multiplePhotos(Session, images, name, typeId):
    if not images:
        return
    for image in images:
        print(image.filename)
        link = uploadToGcs(image,"/sponser/{name}/{image.filename}")
        sponser = Sponser(link= link,typeId=typeId)
        session.add(sponser)

def addType(body):
    name = body.get("name")
    if not name:
        raise PecfestException(statusCode=301, message="Provide category name")

    with DBConnectionManager() as session:
        try:
            sponserType = SponserType(name=name)
            session.add(sponserType)
            session.commit()

            images = body.get("photos")
            if images:
                multiplePhotos(session, images, name, sponserType.id)
            session.commit()
        except Exception as e:
            logger.info(f"Err: Add Sponser type {e}")
            raise PecfestException()

    return {"status": "Success", "statusCode":200, "message": "Event type added successfully"}

def addSponser(body):
    removed = body.get("removed")
    added = body.get("added")
    
    with DBConnectionManager() as session:
        if removed and len(removed):
            sponsers = session.query(Sponser).filter(Sponser.id.in_(removed)).all()
            for sponser in sponsers:
                sponser.isDeleted = True

        if added:
            name = added.get("typeName")
            if not name:
                raise PecfestException(statusCode=301, message="Please provide Sponser Type name")
            id = added.get("typeId")
            if not id:
                raise PecfestException(statusCode=301, message="Please provide Sponser type id")
            images = added.get("images")
            if not images or not len(images):
                raise PecfestException(statusCode=301, message="Please provide sponsers image")
            multiplePhotos(session, images, name, id)

        session.commit()
    
    return {"status": "SUCCESS", "statusCode": 200, "message": "Sponsers edited successfully"}

