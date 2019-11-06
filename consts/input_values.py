from collections import namedtuple

ACCOUNT_EMAIL_DEFAULT = 'kgoautomation@gmail.com'
ACCOUNT_NAME_DEFAULT = 'Kenneth Automation'
ACCOUNT_NAME_SHORT = 'K'
EMAIL_PASSWORD = 'LivePlanet16!'
ACCOUNT_PASSWORD_TOO_SHORT = '2short'
ACCOUNT_PASSWORD_NO_NUMBERS = 'nonumbers'
ACCOUNT_PASSWORD_NO_LETTERS = '1234567890'
ACCOUNT_PASSWORD_DEFAULT = 'tester123'
ACCOUNT_PASSWORD_01 = 'tester1234'
NONEXISTANT_EMAIL = 'not_a_real_email@fake.ru'
INVALID_EMAIL_NO_AT_SIGN = 'bad_email_format'
INVALID_PASSWORD = 'not_a_real_password'
SUPPORT_EMAIL = 'support@videocoin.network'
PASSWORD_RECOVERY_SUBJECT = 'Password Recovery'
WITHDRAWL_START_SUBJECT = 'Withdraw Confirmation'
WITHDRAWL_SUCCESSFUL_SUBJECT = 'Withdraw Succeeded'
DEPOSIT_ADDRESS_METAMASK = '0x1C4215Fcf5599173BBbc8cDb9119aE42b44ce2D4'
DEPOSIT_ADDRESS_DUMPSTER = '0x3F8d126aa636B64C919129b42e1fe0C498cEdF5c'
DEPOSIT_ADDRESS_TOO_SHORT = '0x1C4215Fcf5599173BBbc8cDb9119aE42b44ce'

# TODO: Crappy regex pls fix.

EmailBodyRegex = namedtuple('EmailBodyRegex', 'name, pattern')
PASSWORD_RECOVERY_REGEX = EmailBodyRegex(
    'password_recovery_regex', r'Password Reset[\S\s]*(https://.*sendgrid.net.*)" t'
)
ETHERSCAN_REGEX = EmailBodyRegex(
    'etherscan_regex', r'Etherscan[\S\s]*(https://.*sendgrid.net.*)" t'
)
VID_TRANSFER_AMOUNT_REGEX = EmailBodyRegex(
    'vid_transfer_amount_regex', r'(\d+\.\d+).*VID'
)
DEPOSIT_ADDRESS_REGEX = EmailBodyRegex('deposit_address_regex', r'(0x[A-Za-z0-9]{40})')
CONFIRMATION_CODE_REGEX = EmailBodyRegex(
    'six_digit_code_regex', r'Copy the 6 digit code below [\S\s]* ([0-9]{6})'
)
