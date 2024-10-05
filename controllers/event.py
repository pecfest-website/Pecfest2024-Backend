from tables import Event, DBConnectionManager
from sqlalchemy.orm import joinedload, noload

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
