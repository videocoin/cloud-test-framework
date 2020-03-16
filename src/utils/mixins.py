import pytest
import math
import logging
import requests


from src.consts.input_values import VALUES, VID_TOKEN_ADDR, FAUCET_URL


logger = logging.getLogger(__name__)


class VideocoinMixin:

    @pytest.fixture(autouse=True)
    def init_cluster(self, cluster):
        self.cluster = cluster

    def get_initial_value(self, variable):
        return VALUES[self.cluster][variable]

    def get_vid_balance_of_erc20(self, w3, abi, addr):
        token_addr = self.get_initial_value(VID_TOKEN_ADDR)
        vid_addr = w3.eth.contract(token_addr, abi=abi)
        amt = vid_addr.functions.balanceOf(w3.toChecksumAddress(addr)).call()

        return amt

    def faucet_vid_to_account(self, address, amount):
        if type(amount) == float:
            amount = int(math.ceil(amount))
            logger.debug(
                'Cannot send float VID amount to address. '
                'Converting float value to integer'
            )

        body = {'account': address, 'amount': amount}
        for x in range(5):
            res = requests.post(
                self.get_initial_value(FAUCET_URL),
                json=body,
            )
            if res.status_code == 200:
                break
        else:
            res.raise_for_status()
