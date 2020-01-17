from datetime import datetime
import logging
from time import sleep

from utils import utils
from consts import input_values

logger = logging.getLogger(__name__)


def test_bank_receives_correct_amount(w3, abi, user):
    deposit_amt = 10 * 10 ** 18
    vid_token_addr = '0x22f9830cfCa475143749f19Ca7d5547D4939Ff67'
    sender = input_values.DEPOSIT_ADDRESS_METAMASK
    sender_private_key = input_values.PRIVATE_KEY_METAMASK
    timeout = 360

    vid_contract = w3.eth.contract(vid_token_addr, abi=abi)
    start_amt = utils.get_vid_balance_of_erc20(w3, abi, input_values.RINKEBY_VID_BANK)
    vid_txn = vid_contract.functions.transfer(
        user.wallet_address, deposit_amt
    ).buildTransaction(
        {
            'chainId': 4,
            'gas': 200000,
            'value': 0,
            'gasPrice': 1000000000,
            'nonce': w3.eth.getTransactionCount(sender),
        }
    )
    signed_txn = w3.eth.account.signTransaction(vid_txn, sender_private_key)
    w3.eth.sendRawTransaction(signed_txn.rawTransaction)

    latest_amt = utils.get_vid_balance_of_erc20(w3, abi, input_values.RINKEBY_VID_BANK)
    logger.debug('Latest VID balance: {}'.format(latest_amt))
    start_time = datetime.now()
    while start_amt == latest_amt:
        if utils.time_from_start(start_time) > timeout:
            raise RuntimeError(
                'Took too long for bank to receive VID. Timeout allowed: {}'.format(
                    timeout
                )
            )
        latest_amt = utils.get_vid_balance_of_erc20(
            w3, abi, input_values.RINKEBY_VID_BANK
        )
        logger.debug('Latest VID balance: {}'.format(latest_amt))
        sleep(1)

    end_amt = latest_amt
    end_time = datetime.now()
    logger.debug('Start VID balance: {:.6e}'.format(start_amt))
    logger.debug('End VID balance: {:.6e}'.format(end_amt))
    logger.debug('VID difference from start to end: {:.6e}'.format(end_amt - start_amt))
    logger.debug(
        'Time elapsed for bank to receive VID: {}'.format(end_time - start_time)
    )
    assert end_amt - start_amt == deposit_amt
