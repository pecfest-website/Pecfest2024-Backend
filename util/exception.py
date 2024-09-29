class PecfestException(Exception):
    def __init__(self, status: str = 'FAILED', statusCode: int = 400, message: str = "Some error occured. Contact developers for help"):
        super().__init__(message)
        self.status = status
        self.statusCode = statusCode
        self.message = message

    def to_dict(self):
        return {
            "status": self.status,
            "statusCode": self.statusCode,
            "message": self.message
        }