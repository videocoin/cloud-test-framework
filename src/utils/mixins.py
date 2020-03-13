import pytest

from src.consts.input_values import VALUES, VID_TOKEN_ADDR


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
