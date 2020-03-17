from datetime import datetime
import logging
from time import sleep
import pytest

from src.utils.mixins import VideocoinMixin
from src.utils import utils
from src.consts.input_values import (VID_TOKEN_ADDR, DEPOSIT_ADDRESS_METAMASK, PRIVATE_KEY_METAMASK, RINKEBY_VID_BANK)

logger = logging.getLogger(__name__)


class TestBank(VideocoinMixin):

    @pytest.mark.smoke
    def test_bank_receives_correct_amount(self, w3, abi, user):
        """
        Check correct erc20 token transfer for bank account
        """
        deposit_amt = 10 * 10 ** 18
        vid_token_addr = self.get_initial_value(VID_TOKEN_ADDR)
        sender = self.get_initial_value(DEPOSIT_ADDRESS_METAMASK)
        sender_private_key = self.get_initial_value(PRIVATE_KEY_METAMASK)
        timeout = 60
        vid_contract = w3.eth.contract(vid_token_addr, abi=abi)
        start_amt = self.get_vid_balance_of_erc20(w3, abi, self.get_initial_value(RINKEBY_VID_BANK))
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

        latest_amt = self.get_vid_balance_of_erc20(
            w3, abi, self.get_initial_value(RINKEBY_VID_BANK)
        )
        logger.debug('Latest VID balance: {}'.format(latest_amt))
        start_time = datetime.now()
        while start_amt == latest_amt:
            if utils.time_from_start(start_time) > timeout:
                raise RuntimeError(
                    'Took too long for bank to receive VID. Timeout allowed: {}'.format(
                        timeout
                    )
                )
            latest_amt = self.get_vid_balance_of_erc20(
                w3, abi, self.get_initial_value(RINKEBY_VID_BANK)
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
