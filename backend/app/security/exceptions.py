class AuthenticationRequiredError(Exception):
    def __init__(self, message: str = "Not authenticated"):
        self.message = message
        super().__init__(message)


class InvalidTokenError(Exception):
    def __init__(self, message: str = "Invalid token"):
        self.message = message
        super().__init__(message)


class PermissionDeniedError(Exception):
    def __init__(self, message: str = "Forbidden"):
        self.message = message
        super().__init__(message)
