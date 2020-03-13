from datetime import datetime
from time import sleep
import pytest
import logging

from src.consts import input_values
from src.utils import utils

logger = logging.getLogger(__name__)


class TestBank:
    def test_deposit_updates_eth_acct_balance_correctly(self, user, w3, abi):
        """
        Check correct erc20 token transfer between users
        """
        deposit_amt = 10 * 10 ** 18
        eth_addr = input_values.DEPOSIT_ADDRESS_METAMASK
        eth_private_key = input_values.PRIVATE_KEY_METAMASK
        timeout = 300

        vid_contract = w3.eth.contract(input_values.VID_TOKEN_ADDR, abi=abi)
        start_amt = utils.get_vid_balance_of_erc20(w3, abi, eth_addr)
        vid_txn = vid_contract.functions.transfer(
            user.wallet_address, deposit_amt
        ).buildTransaction(
            {
                'chainId': 4,
                'gas': 200000,
                'value': 0,
                'gasPrice': 1000000000,
                'nonce': w3.eth.getTransactionCount(eth_addr),
            }
        )
        signed_txn = w3.eth.account.signTransaction(vid_txn, eth_private_key)
        w3.eth.sendRawTransaction(signed_txn.rawTransaction)

        start_time = datetime.now()
        latest_amt = utils.get_vid_balance_of_erc20(w3, abi, eth_addr)
        while start_amt == latest_amt:
            if utils.time_from_start(start_time) > timeout:
                raise RuntimeError(
                    'Took too long to subtract funds. Timeout allowed: {}'.format(timeout)
                )
            latest_amt = utils.get_vid_balance_of_erc20(w3, abi, eth_addr)
            sleep(1)

        end_amt = latest_amt
        logger.debug('Start VID balance: {:.6e}'.format(start_amt))
        logger.debug('End VID balance: {:.6e}'.format(end_amt))
        logger.debug('VID difference from start to end: {:.6e}'.format(end_amt))
        logger.debug('Duration to subtract funds: {}'.format(datetime.now() - start_time))

        assert start_amt - end_amt == deposit_amt

    @pytest.mark.skip('in progress')
    def test_deposit_updates_vid_acct_balance_correctly(self, user, w3, abi):
        """
        Check correct erc20 token transfer
        """
        start_amt = user.wallet_balance
        deposit_amt = 10 * 10 ** 18

        vid_contract = w3.eth.contract(input_values.VID_TOKEN_ADDR, abi=abi)
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
    def test_time_before_deposit_funds_received(self, user, w3, abi):
        times = []
        for i in range(5):
            start_amt = user.wallet_balance
            deposit_amt = 10 * 10 ** 18

            vid_contract = w3.eth.contract(input_values.VID_TOKEN_ADDR, abi=abi)
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
