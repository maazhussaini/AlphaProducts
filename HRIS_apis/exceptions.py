class ValidationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class NotFoundError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class DatabaseError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class LeaveRequestError(Exception):
    """Base class for exceptions in this module."""
    pass

class AttendanceConflictError(LeaveRequestError):
    """Exception raised for conflicts with existing attendance."""
    def __init__(self, message):
        self.message = message

class DuplicateLeaveError(LeaveRequestError):
    """Exception raised for duplicate leave requests."""
    def __init__(self, message):
        self.message = message

class InvalidLeaveDateError(LeaveRequestError):
    """Exception raised for invalid date ranges."""
    def __init__(self, message):
        self.message = message

class InsufficientLeaveError(LeaveRequestError):
    """Exception raised for insufficient leave balance."""
    def __init__(self, message):
        self.message = message
