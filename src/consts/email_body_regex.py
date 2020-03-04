from collections import namedtuple

EmailBodyRegex = namedtuple('EmailBodyRegex', 'name, pattern')
PASSWORD_RECOVERY_REGEX = EmailBodyRegex(
    'password_recovery_regex', r'Password Reset[\S\s]*(https://.*sendgrid.net.*)" t'
)
ETHERSCAN_REGEX = EmailBodyRegex(
    'etherscan_regex', r'Etherscan[\S\s]*(https://.*sendgrid.net.*)" t'
)
VID_TRANSFER_AMOUNT_REGEX = EmailBodyRegex(
    'vid_transfer_amount_regex', r'(\d+\.?\d*).*VID'
)
DEPOSIT_ADDRESS_REGEX = EmailBodyRegex('deposit_address_regex', r'(0x[A-Za-z0-9]{40})')
CONFIRMATION_CODE_REGEX = EmailBodyRegex(
    'six_digit_code_regex', r'Copy the 6 digit code below [\S\s]* ([0-9]{6})'
)
