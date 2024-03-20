from fastapi.exceptions import RequestValidationError


def validation_error(error_message: str, location: tuple[str, str]) -> RequestValidationError:
    return RequestValidationError(errors=[{"msg": error_message, "loc": location, "type": "value_error"}])
