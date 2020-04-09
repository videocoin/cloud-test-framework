SIGN_IN_WITH_NON_EXISTENT_EMAIL_ERROR = {
    'message': 'Authentication failed',
    'fields': None,
}
SIGN_IN_WITH_INCORRECT_PASSWORD_ERROR = {
    'message': 'Authentication failed',
    'fields': None,
}
CREATE_STREAM_WITH_EMPTY_NAME_ERROR = {
    'message': 'invalid argument',
    'fields': {'name': 'Name is a required field'},
}
CREATE_STREAM_WITH_EMPTY_PROFILE_ID_ERROR = {
    'message': 'invalid argument',
    'fields': {'profile_id': 'ProfileId is a required field'},
}
SIGN_UP_WITH_EXISTING_EMAIL_ERROR = {
    'message': 'invalid argument',
    'fields': {'email': 'Email is already registered'},
}
SIGN_UP_WITH_SHORT_NAME_ERROR = {
    'message': 'invalid argument',
    'fields': {'name': 'Name must be at least 2 characters in length'},
}
SIGN_UP_WITH_INVALID_PASSWORD = {
    'message': 'invalid argument',
    'fields': {
        'password': 'Password must be more than 8 characters and contain both numbers and letters'
    },
}
INCORRECT_CONFIRMATION_CODE_ERROR = {'message': 'Bad request', 'fields': None}
