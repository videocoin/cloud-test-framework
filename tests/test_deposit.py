from datetime import datetime
from time import sleep
import pytest
import logging

from consts import input_values
from utils import utils

logger = logging.getLogger(__name__)


@pytest.mark.skip('need to fix get_vid_balance_of_erc20() first')
def test_deposit_updates_eth_acct_balance_correctly(user, w3, abi):
    deposit_amt = 10 * 10 ** 18

    vid_token_addr = '0x22f9830cfCa475143749f19Ca7d5547D4939Ff67'
    vid_contract = w3.eth.contract(vid_token_addr, abi=abi)
    start_amt = utils.get_vid_balance_of_erc20()
    vid_txn = vid_contract.functions.transfer(
        user.wallet_address, deposit_amt
    ).buildTransaction(
        {
            'chainId': 4,
            'gas': 200000,
            'value': 0,
            'gasPrice': 1000000000,
            'nonce': w3.eth.getTransactionCount(input_values.DEPOSIT_ADDRESS_METAMASK),
        }
    )
    private_key = '523FC9D14D9610691BE281348968976FD397788EED49B1DB8949005ECA85B2E0'
    signed_txn = w3.eth.account.signTransaction(vid_txn, private_key)
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(txn_hash.hex())

    # start_time = datetime.now()
    sleep(300)
    end_amt = user.wallet_balance

    # while start_amt == end_amt:
    #     end_amt = user.wallet_balance
    #     sleep(1)

    logger.debug('Start VID balance: {:.6e}'.format(start_amt))
    logger.debug('End VID balance: {:.6e}'.format(end_amt))
    # logger.debug('Duration to receive funds: {}'.format(start_time - datetime.now()))


@pytest.mark.skip('in progress')
def test_deposit_updates_vid_acct_balance_correctly(user, w3, abi):
    start_amt = user.wallet_balance
    deposit_amt = 10 * 10 ** 18

    vid_token_addr = '0x22f9830cfCa475143749f19Ca7d5547D4939Ff67'
    vid_contract = w3.eth.contract(vid_token_addr, abi=abi)
    vid_txn = vid_contract.functions.transfer(
        user.wallet_address, deposit_amt
    ).buildTransaction(
        {
            'chainId': 4,
            'gas': 200000,
            'value': 0,
            'gasPrice': 1000000000,
            'nonce': w3.eth.getTransactionCount(input_values.DEPOSIT_ADDRESS_METAMASK),
        }
    )
    private_key = '523FC9D14D9610691BE281348968976FD397788EED49B1DB8949005ECA85B2E0'
    signed_txn = w3.eth.account.signTransaction(vid_txn, private_key)
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(txn_hash.hex())

    start_time = datetime.now()
    sleep(300)
    end_amt = user.wallet_balance

    # while start_amt == end_amt:
    #     end_amt = user.wallet_balance
    #     sleep(1)

    logger.debug('Start VID balance: {:.6e}'.format(start_amt))
    logger.debug('End VID balance: {:.6e}'.format(end_amt))
    # logger.debug('Duration to receive funds: {}'.format(start_time - datetime.now()))


@pytest.mark.skip('in progress')
def test_time_before_deposit_funds_received(user, w3, abi):
    times = []
    for i in range(5):
        start_amt = user.wallet_balance
        deposit_amt = 10 * 10 ** 18

        vid_token_addr = '0x22f9830cfCa475143749f19Ca7d5547D4939Ff67'
        vid_contract = w3.eth.contract(vid_token_addr, abi=abi)
        vid_txn = vid_contract.functions.transfer(
            user.wallet_address, deposit_amt
        ).buildTransaction(
            {
                'chainId': 4,
                'gas': 200000,
                'value': 0,
                'gasPrice': 1000000000,
                'nonce': w3.eth.getTransactionCount(
                    input_values.DEPOSIT_ADDRESS_METAMASK
                ),
            }
        )
        private_key = '523FC9D14D9610691BE281348968976FD397788EED49B1DB8949005ECA85B2E0'
        signed_txn = w3.eth.account.signTransaction(vid_txn, private_key)
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        logger.debug('tx hash of deposit transfer: {}'.format(txn_hash.hex()))

        start_time = datetime.now()
        end_amt = user.wallet_balance

        while start_amt == end_amt:
            end_amt = user.wallet_balance
            sleep(1)

        end_time = datetime.now()
        logger.debug('Start VID balance: {:.6e}'.format(start_amt))
        logger.debug('End VID balance: {:.6e}'.format(end_amt))
        logger.debug('VID balance diff: {:.6e}'.format(end_amt - start_amt))
        logger.debug('Duration to receive funds: {}'.format(end_time - start_time))
        times.append((end_time - start_time).total_seconds())

    logger.debug('Times for deposit to be received: {}'.format(times))
    logger.debug(
        'Average time for deposit to be received: {}'.format(sum(times) / len(times))
    )
