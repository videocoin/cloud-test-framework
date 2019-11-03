SIGN_IN_WITH_NON_EXISTENT_EMAIL_ERROR = {
    'message': 'Authentication failed',
    'fields': None
}
SIGN_IN_WITH_INCORRECT_PASSWORD_ERROR = {
    'message': 'Authentication failed',
    'fields': None
}
CREATE_STREAM_WITH_EMPTY_NAME_ERROR = {
    'message': 'invalid argument',
    'fields': {
        'name': 'Name is a required field'
    }    
}
CREATE_STREAM_WITH_EMPTY_PROFILE_ID_ERROR = {
    'message': 'invalid argument',
    'fields': {
        'profile_id': 'ProfileId is a required field'
    }
}
PASSWORD_RECOVERY_WITH_NON_EXISTENT_EMAIL_ERROR = {
    'message': 'invalid argument',
    'fields': {
        'email': 'Enter a valid email address'
    }
}
PASSWORD_RECOVERY_WITH_INVALID_EMAIL_ERROR = {
    'message': 'invalid argument',
    'fields': {
        'email': 'Enter a valid email address'
    }
}
SIGN_UP_WITH_EXISTING_EMAIL_ERROR = {
    'message': 'invalid argument',
    'fields': {
        'email': 'Email is already registered'
    }
}
SIGN_UP_WITH_SHORT_NAME_ERROR = {
    'message': 'invalid argument',
    'fields': {
        'name': 'Name must be at least 2 characters in length'
    }
}
SIGN_UP_WITH_INVALID_PASSWORD = {
    'message': 'invalid argument',
    'fields': {
        'password': 'Password must be more than 8 characters and contain both numbers and letters'
    }
}
# TODO: Don't compare the commented out valeus for now, since they're constantly changing
# Need to find a way to not compare these values, but make sure they're in the right format
TEST_USER_INFORMATION = {
  'id': 'd71b8961-8de3-4383-7ac0-46299d2186f5',
  'email': 'kgoautomation@gmail.com',
  'name': 'Kenneth Go',
  'is_active': True,
  'account': {
    'id': '25237a3c-d0bc-45d2-75c8-3f835f0012e3',
    'address': '0x003d07A64C2FeFc8C1654EF742F9AF4088354090',
    # 'balance': 1308,
    # 'updated_at': '2019-10-31T23:00:12.604164461Z'
  }
}
NEW_STREAM_INFORMATION = {
  'id': '93f9512c-e524-4027-45a3-7e96c62ac0ff',
  'name': 'asdf',
  'input_url': 'http://rtmp.studio.snb.videocoin.network/hls/93f9512c-e524-4027-45a3-7e96c62ac0ff/index.m3u8',
  'output_url': 'https://streams-snb.videocoin.network/93f9512c-e524-4027-45a3-7e96c62ac0ff/index.m3u8',
  'stream_contract_id': '8307372028691654424',
  'stream_contract_address': '',
  'status': 'STREAM_STATUS_NEW',
  'input_status': 'INPUT_STATUS_NONE',
  'created_at': '2019-10-31T23:49:05Z',
  'updated_at': '2019-10-31T23:49:05Z',
  'ready_at': None,
  'completed_at': None,
  'rtmp_url': 'rtmp://rtmp.studio.snb.videocoin.network:1935/live/93f9512c-e524-4027-45a3-7e96c62ac0ff'
}
