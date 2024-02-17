class OutlineError(Exception):
    errors = {}

    def __init__(self, status_code):
        self.status_code = status_code

    def __str__(self):
        return f"{self.errors[self.status_code]}"


class OutlineTelemetryError(OutlineError):
    errors = {
        400: "Invalid request"
    }


class OutlineInvalidName(OutlineError):
    errors = {
        400: "Invalid name",
        204: "OK"
    }


class OutlineInvalidHostname(OutlineError):
    errors = {
        400: "An invalid hostname or IP address was provided.",
        500: """An internal error occurred. 
        This could be thrown if there were network errors while validating the hostname"""
    }


class OutlinePortError(OutlineError):
    errors = {
        400: """The requested port wasn't an integer from 1 through 65535, 
        or the request had no port parameter.""",
        409: "The requested port was already in use by another service."
    }


class OutlineInvalidDataLimit(OutlineError):
    errors = {
        400: "Invalid data limit",
        404: "Access key inexistent"
    }


class OutlineInvalidAccessKey(OutlineError):
    errors = {
        404: "Access key inexistent"
    }
