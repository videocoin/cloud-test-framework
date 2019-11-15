import logging
import pytest
import random
import requests
from time import sleep

from consts import input_values
from consts import email_body_regex
from utils import utils

logger = logging.getLogger(__name__)


@pytest.mark.smoke
@pytest.mark.functional
def test_starting_withdraw_with_valid_address_and_amount_has_correct_information(user):
    """
    Name:
    Starting withdraw with valid address and amount has correct information

    Description:
    When the user begins a withdraw process to deposit to a valid address and has a
    valid withdraw amount, the information in the withdraw confirmation email should
    be correct and accurately reflect the information that initiated the withdraw.

    Steps:
    0. Initiate withdraw request from server, noting the address and amount submitted
    0. Check email for withdraw confirmation email, note the information listed in email
    0. Compare submitted information to information in confirmation email

    Expected results:
    0. Information listed in email is accurate compared to information submitted
    """
    deposit_address = input_values.DEPOSIT_ADDRESS_METAMASK
    email = user.email
    email_password = user.email_password

    utils.send_vid_to_account(user.wallet_address, 20)
    user.start_withdraw(deposit_address, 20)
    # TODO: Replace with waiting until the newly sent (unread) email is found in inbox
    sleep(5)
    withdraw_info = _get_withdraw_confirmation_email_information(email, email_password)

    assert withdraw_info[email_body_regex.VID_TRANSFER_AMOUNT_REGEX.name] == '20.000000'
    assert withdraw_info[email_body_regex.DEPOSIT_ADDRESS_REGEX.name] == deposit_address
    assert len(withdraw_info[email_body_regex.CONFIRMATION_CODE_REGEX.name]) == 6


@pytest.mark.functional
@pytest.mark.parametrize(
    'invalid_code, expected_error',
    [
        (
            '',
            {
                'message': 'invalid argument',
                'fields': {'pin': 'Pin is a required field'},
            },
        ),
        ('asdf56', {'message': 'Bad request', 'fields': None}),
        (
            '123',
            {
                "message": "invalid argument",
                "fields": {"pin": "Pin must be 6 characters in length"},
            },
        ),
        (
            '123456789',
            {
                "message": "invalid argument",
                "fields": {"pin": "Pin must be 6 characters in length"},
            },
        ),
    ],
)
def test_invalid_confirmation_code_returns_error(user, invalid_code, expected_error):
    deposit_address = input_values.DEPOSIT_ADDRESS_METAMASK
    vid_to_withdraw = 20.0
    email = user.email
    email_password = user.email_password

    utils.send_vid_to_account(user.wallet_address, vid_to_withdraw)
    transfer_id = user.start_withdraw(deposit_address, vid_to_withdraw)
    # Used to delete the sent emails, but no information is needed
    # TODO: Replace with waiting until the newly sent (unread) email is found in inbox
    sleep(5)
    _ = _get_withdraw_confirmation_email_information(email, email_password)
    with pytest.raises(requests.HTTPError) as e:
        user.confirm_withdraw(transfer_id, invalid_code)

    assert e.value.response.status_code == 400
    assert e.value.response.json() == expected_error


@pytest.mark.smoke
@pytest.mark.functional
def test_correct_confirmation_code_sends_success_email(user):
    deposit_address = input_values.DEPOSIT_ADDRESS_METAMASK
    vid_to_withdraw = 20.0
    email = user.email
    email_password = user.email_password

    utils.send_vid_to_account(user.wallet_address, vid_to_withdraw)
    transfer_id = user.start_withdraw(deposit_address, vid_to_withdraw)
    # TODO: Replace with waiting until the newly sent (unread) email is found in inbox
    sleep(5)
    withdraw_info = _get_withdraw_confirmation_email_information(email, email_password)
    confirmation_code = withdraw_info[email_body_regex.CONFIRMATION_CODE_REGEX.name]
    user.confirm_withdraw(transfer_id, confirmation_code)

    # The time it takes for the withdraw process to complete varies fairly widely
    # Try getting the success email a few times before timing out and giving error
    tries = 0
    while tries < 5:
        try:
            logger.debug('trying to get success email, attempt #{}'.format(tries))
            sleep(5)
            email_info = _get_withdraw_successful_email_information(
                email, email_password
            )
            break
        except IndexError as e:
            tries += 1
            if tries <= 5:
                continue
            else:
                raise e

    assert (
        float(email_info[email_body_regex.VID_TRANSFER_AMOUNT_REGEX.name])
        == vid_to_withdraw
    )
    assert email_info[email_body_regex.DEPOSIT_ADDRESS_REGEX.name] == deposit_address
    assert email_info[email_body_regex.ETHERSCAN_REGEX.name]


@pytest.mark.functional
def test_entering_incorrect_confirmation_code_returns_error(user):
    email = user.email
    email_password = user.email_password
    deposit_address = input_values.DEPOSIT_ADDRESS_METAMASK

    utils.send_vid_to_account(user.wallet_address, 20)
    transfer_id = user.start_withdraw(deposit_address, 20)
    # TODO: Replace with waiting until the newly sent (unread) email is found in inbox
    sleep(5)
    withdraw_info = _get_withdraw_confirmation_email_information(email, email_password)
    real_confirmation_code = withdraw_info[
        email_body_regex.CONFIRMATION_CODE_REGEX.name
    ]
    incorrect_confirmation_code = _create_random_confirmation_code()
    while real_confirmation_code == incorrect_confirmation_code:
        # No way this'll happen lol
        logger.warning('Holy shit it happened')
        incorrect_confirmation_code == _create_random_confirmation_code()

    logger.debug('transfer_id: %s', transfer_id)
    logger.debug('real_confirmation_code: %s', real_confirmation_code)
    logger.debug('incorrect_confirmation_code: %s', incorrect_confirmation_code)

    with pytest.raises(requests.HTTPError) as e:
        user.confirm_withdraw(transfer_id, incorrect_confirmation_code)

    assert e.value.response.status_code == 400
    assert e.value.response.json() == {'message': 'Bad request', 'fields': None}


# def test_many_withdraws_at_once(users):
#     for user in users:
#         print(user.email)


# This should return an error, currently gives a valid transfer_id
@pytest.mark.skip
@pytest.mark.functional
def test_starting_withdraw_with_invalid_address_format_returns_error(user):
    # try:
    #     DEPOSIT_ADDRESS_INVALID = 'aasdfff0x03948593jcns456fsc52j358dsjsf4499'
    #     utils.send_vid_to_account(user.wallet_address, 20)
    #     # withdraw_id = user.start_withdraw(DEPOSIT_ADDRESS_INVALID, 20)
    # finally:
    #     # should be able to throw the rest of the VID away, to clean the account
    #     pass
    pass


# This should return an error, currently gives a valid transfer_id
@pytest.mark.skip
@pytest.mark.functional
def test_starting_withdraw_with_unavailable_amount_of_vid(user):
    # withdraw_id = user.start_withdraw(input_values.DEPOSIT_ADDRESS_METAMASK, 9999)
    pass


def _get_withdraw_confirmation_email_information(email, email_password):
    subject = 'Withdraw Confirmation'
    return utils.get_items_from_email(
        email,
        email_password,
        subject,
        email_body_regex.VID_TRANSFER_AMOUNT_REGEX,
        email_body_regex.DEPOSIT_ADDRESS_REGEX,
        email_body_regex.CONFIRMATION_CODE_REGEX,
    )


def _get_withdraw_successful_email_information(email, email_password):
    subject = 'Withdraw Succeeded'
    return utils.get_items_from_email(
        email,
        email_password,
        subject,
        email_body_regex.VID_TRANSFER_AMOUNT_REGEX,
        email_body_regex.DEPOSIT_ADDRESS_REGEX,
        email_body_regex.ETHERSCAN_REGEX,
    )


def _remove_all_vid_from_account(user):
    pass


def _create_random_confirmation_code(length=6):
    random_confirmation_code = ''
    for i in range(length):
        random_confirmation_code += str(random.randrange(10))

    return random_confirmation_code
