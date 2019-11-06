import logging 
import pytest
import random
import requests
from time import sleep

from consts import expected_results
from consts import input_values
from utils import utils

logger = logging.getLogger(__name__)

def test_starting_withdraw_with_valid_address_and_amount_is_correct(user):
    utils.send_vid_to_account(user.wallet_address, 20)
    user.start_withdraw(input_values.DEPOSIT_ADDRESS_METAMASK, 20)
    # TODO: Replace with waiting until the newly sent (unread) email is found in inbox
    sleep(5)
    withdraw_info = _get_withdraw_start_email_information(
        input_values.ACCOUNT_EMAIL_DEFAULT, input_values.EMAIL_PASSWORD)

    assert withdraw_info[input_values.VID_TRANSFER_AMOUNT_REGEX.name] == '20.000000'
    assert withdraw_info[input_values.DEPOSIT_ADDRESS_REGEX.name] == input_values.DEPOSIT_ADDRESS_METAMASK
    assert len(withdraw_info[input_values.CONFIRMATION_CODE_REGEX.name]) == 6

def test_entering_correct_confirmation_code_sends_success_email(user):
    deposit_address = input_values.DEPOSIT_ADDRESS_METAMASK
    vid_to_withdraw = 20.0
    email = input_values.ACCOUNT_EMAIL_DEFAULT
    email_password = input_values.EMAIL_PASSWORD

    utils.send_vid_to_account(user.wallet_address, vid_to_withdraw)
    transfer_id = user.start_withdraw(deposit_address, vid_to_withdraw)
    # TODO: Replace with waiting until the newly sent (unread) email is found in inbox
    sleep(5)
    withdraw_info = _get_withdraw_start_email_information(email, email_password)
    confirmation_code = withdraw_info[input_values.CONFIRMATION_CODE_REGEX.name]
    user.confirm_withdraw(transfer_id, confirmation_code)
    tries = 0
    while tries < 5:
        try:
            logger.debug('trying to get success email, attempt #{}'.format(tries))
            sleep(5)            
            tries += 1
            email_info = _get_withdraw_successful_email_information(email, email_password)
            break
        except IndexError as e:
            if tries <= 5:
                continue
            else:
                raise e

    assert float(email_info[input_values.VID_TRANSFER_AMOUNT_REGEX.name]) == vid_to_withdraw
    assert email_info[input_values.DEPOSIT_ADDRESS_REGEX.name] == deposit_address
    assert email_info[input_values.ETHERSCAN_REGEX.name]

def test_entering_incorrect_confirmation_code_returns_error(user):
    utils.send_vid_to_account(user.wallet_address, 20)
    transfer_id = user.start_withdraw(input_values.DEPOSIT_ADDRESS_METAMASK, 20)
    # TODO: Replace with waiting until the newly sent (unread) email is found in inbox
    sleep(5)
    withdraw_info = _get_withdraw_start_email_information(
        input_values.ACCOUNT_EMAIL_DEFAULT, input_values.EMAIL_PASSWORD)
    real_confirmation_code = withdraw_info[input_values.CONFIRMATION_CODE_REGEX.name]
    incorrect_confirmation_code = _create_random_confirmation_code()
    while real_confirmation_code == incorrect_confirmation_code:
        # No way this'll happen lol
        incorrect_confirmation_code == _create_random_confirmation_code()
    logger.debug('transfer_id: %s', transfer_id)
    logger.debug('real_confirmation_code: %s', real_confirmation_code)
    logger.debug('incorrect_confirmation_code: %s', incorrect_confirmation_code)

    with pytest.raises(requests.HTTPError) as e: 
        user.confirm_withdraw(transfer_id, incorrect_confirmation_code)

    assert e.value.response.status_code == 400
    assert e.value.response.json() == expected_results.INCORRECT_CONFIRMATION_CODE_ERROR

# This should return an error, currently gives a valid transfer_id
@pytest.mark.skip
def test_starting_withdraw_with_invalid_address_format_returns_error(user):
    try:
        DEPOSIT_ADDRESS_INVALID = 'aasdfff0x03948593jcns456fsc52j358dsjsf4499'
        utils.send_vid_to_account(user.wallet_address, 20)
        withdraw_id = user.start_withdraw(DEPOSIT_ADDRESS_INVALID, 20)
    finally:
        # should be able to throw the rest of the VID away, to clean the account
        pass

# This should return an error, currently gives a valid transfer_id
@pytest.mark.skip
def test_starting_withdraw_with_unavailable_amount_of_vid(user):
    withdraw_id = user.start_withdraw(input_values.DEPOSIT_ADDRESS_METAMASK, 9999)

def _get_withdraw_start_email_information(email, email_password):
    return utils.get_items_from_email(email, email_password, 
        input_values.WITHDRAWL_START_SUBJECT,
        input_values.VID_TRANSFER_AMOUNT_REGEX,
        input_values.DEPOSIT_ADDRESS_REGEX,
        input_values.CONFIRMATION_CODE_REGEX)

def _get_withdraw_successful_email_information(email, email_password):
    return utils.get_items_from_email(email, email_password,
        input_values.WITHDRAWL_SUCCESSFUL_SUBJECT,
        input_values.VID_TRANSFER_AMOUNT_REGEX,
        input_values.DEPOSIT_ADDRESS_REGEX,
        input_values.ETHERSCAN_REGEX)

def _remove_all_vid_from_account(user):
    pass

def _create_random_confirmation_code(length=6):
    random_confirmation_code = ''
    for i in range(length):
        random_confirmation_code += str(random.randrange(10))

    return random_confirmation_code
