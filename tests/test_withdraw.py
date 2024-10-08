import logging
import pytest
import random
import requests
from time import sleep
from web3.auto import w3

from consts import input_values
from consts import email_body_regex
from utils import utils

logger = logging.getLogger(__name__)


@pytest.mark.smoke
@pytest.mark.functional
def test_starting_withdraw_with_valid_address_and_amount_has_correct_information(user):
    deposit_address = input_values.DEPOSIT_ADDRESS_METAMASK
    withdraw_amt = 20
    withdraw_amt_wei = w3.toWei(withdraw_amt, 'ether')
    email = user.email
    email_password = user.email_password

    utils.faucet_vid_to_account(user.wallet_address, withdraw_amt)
    user.start_withdraw(deposit_address, withdraw_amt_wei)
    # TODO: Replace with waiting until the newly sent (unread) email is found in inbox
    sleep(5)
    withdraw_info = _get_withdraw_confirmation_email_information(email, email_password)

    assert withdraw_info[email_body_regex.VID_TRANSFER_AMOUNT_REGEX.name] == '20'
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
    withdraw_amt = 20
    withdraw_amt_wei = w3.toWei(withdraw_amt, 'ether')
    email = user.email
    email_password = user.email_password

    utils.faucet_vid_to_account(user.wallet_address, withdraw_amt)
    transfer_id = user.start_withdraw(deposit_address, withdraw_amt_wei)
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
    withdraw_amt = 20
    withdraw_amt_wei = w3.toWei(withdraw_amt, 'ether')
    email = user.email
    email_password = user.email_password

    utils.faucet_vid_to_account(user.wallet_address, withdraw_amt)
    transfer_id = user.start_withdraw(deposit_address, withdraw_amt_wei)
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

    if type(withdraw_amt) == int:
        assert (
            int(email_info[email_body_regex.VID_TRANSFER_AMOUNT_REGEX.name])
            == withdraw_amt
        )
    elif type(withdraw_amt) == float:
        assert (
            float(email_info[email_body_regex.VID_TRANSFER_AMOUNT_REGEX.name])
            == withdraw_amt
        )
    assert email_info[email_body_regex.DEPOSIT_ADDRESS_REGEX.name] == deposit_address
    assert email_info[email_body_regex.ETHERSCAN_REGEX.name]


@pytest.mark.smoke
def test_correct_vid_amount_is_subtracted_from_user_balance(user):
    deposit_address = input_values.DEPOSIT_ADDRESS_METAMASK
    withdraw_amt = 20
    email = user.email
    email_password = user.email_password
    withdraw_amt_wei = w3.toWei(withdraw_amt, 'ether')

    utils.faucet_vid_to_account(user.wallet_address, withdraw_amt)
    # Wait for faucet to send VID to account
    sleep(90)
    start_balance = user.wallet_balance
    transfer_id = user.start_withdraw(deposit_address, withdraw_amt_wei)
    # Wait for confirmation email to be sent
    sleep(10)
    withdraw_info = _get_withdraw_confirmation_email_information(email, email_password)
    confirmation_code = withdraw_info[email_body_regex.CONFIRMATION_CODE_REGEX.name]
    user.confirm_withdraw(transfer_id, confirmation_code)
    # Wait for transaction to finish and be reflected in user's balance
    sleep(90)
    end_balance = user.wallet_balance

    logger.debug('Start balance: {:.6e}'.format(start_balance))
    logger.debug('End balance: {:.6e}'.format(end_balance))
    logger.debug('Withdraw amount (in wei): {:.6e}'.format(withdraw_amt_wei))
    actual_difference = start_balance - end_balance
    expected_difference = withdraw_amt_wei + input_values.NATIVE_GAS_AMOUNT
    assert _is_within_range(actual_difference, expected_difference, 13000)


@pytest.mark.smoke
def test_correct_vid_amount_is_added_to_erc20_addr(user, w3, abi):
    deposit_address = input_values.DEPOSIT_ADDRESS_METAMASK
    withdraw_amt = 20
    email = user.email
    email_password = user.email_password
    withdraw_amt_wei = w3.toWei(withdraw_amt, 'ether')

    logger.debug('withdraw_amt_wei: {}'.format(withdraw_amt_wei))

    start_balance = utils.get_vid_balance_of_erc20(w3, abi, deposit_address)
    utils.faucet_vid_to_account(user.wallet_address, withdraw_amt)
    # Wait for faucet to send VID to account
    sleep(90)
    transfer_id = user.start_withdraw(deposit_address, withdraw_amt_wei)
    # Wait for confirmation email to be sent
    sleep(10)
    withdraw_info = _get_withdraw_confirmation_email_information(email, email_password)
    confirmation_code = withdraw_info[email_body_regex.CONFIRMATION_CODE_REGEX.name]
    user.confirm_withdraw(transfer_id, confirmation_code)
    # Wait for transaction to finish and be reflected in user's balance
    sleep(90)
    end_balance = utils.get_vid_balance_of_erc20(w3, abi, deposit_address)

    logger.debug('Start balance: {}'.format(start_balance))
    logger.debug('End balance: {}'.format(end_balance))
    logger.debug('Withdraw amount (in wei): {}'.format(withdraw_amt_wei))
    logger.debug('Actual difference {}'.format(end_balance - start_balance))
    assert end_balance - start_balance == withdraw_amt_wei


@pytest.mark.functional
@pytest.mark.skip
def test_withdraw_less_than_mainnet_gas(user):
    deposit_address = input_values.DEPOSIT_ADDRESS_METAMASK
    withdraw_amt = 0.5
    withdraw_amt_wei = w3.toWei(withdraw_amt, 'ether')

    utils.faucet_vid_to_account(user.wallet_address, withdraw_amt)
    # Wait for faucet to send VID to account
    sleep(90)
    transfer_id = user.start_withdraw(deposit_address, withdraw_amt_wei)
    # Should fail here


@pytest.mark.functional
def test_entering_incorrect_confirmation_code_returns_error(user):
    email = user.email
    email_password = user.email_password
    deposit_address = input_values.DEPOSIT_ADDRESS_METAMASK
    withdraw_amt = 20
    withdraw_amt_wei = w3.toWei(withdraw_amt, 'ether')

    utils.faucet_vid_to_account(user.wallet_address, 20)
    transfer_id = user.start_withdraw(deposit_address, withdraw_amt_wei)
    # TODO: Replace with waiting until the newly sent (unread) email is found in inbox
    sleep(5)
    withdraw_info = _get_withdraw_confirmation_email_information(email, email_password)
    real_confirmation_code = withdraw_info[
        email_body_regex.CONFIRMATION_CODE_REGEX.name
    ]
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
    #     utils.faucet_vid_to_account(user.wallet_address, 20)
    #     # withdraw_id = user.start_withdraw(DEPOSIT_ADDRESS_INVALID, 20)
    # finally:
    #     # should be able to throw the rest of the VID away, to clean the account
    #     pass
    pass


# This should return an error, currently gives a valid transfer_id
@pytest.mark.skip
@pytest.mark.functional
def test_starting_withdraw_with_unavailable_amount_of_vid(user):
    current_balance = user.wallet_balance
    over_balance = current_balance + w3.fromWei(1000000000000000000, 'ether')
    withdraw_id = user.start_withdraw(
        input_values.DEPOSIT_ADDRESS_METAMASK, over_balance
    )
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


# Withdrawing from an account isn't 100% accurate. Add some tolerance for error
# (measured in wei)
def _is_within_range(actual, expected, tolerance):
    difference = abs(actual - expected)
    logger.debug(
        'Actual difference between actual and expected values: {}'.format(difference)
    )
    logger.debug(
        'Expected difference between actual and expected values: {}'.format(tolerance)
    )
    return abs(actual - expected) <= tolerance
