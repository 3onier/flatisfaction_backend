from rest_framework import exceptions, status

class ChoreAppointmentConflict(exceptions.APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Chore Appointments are conflicting"