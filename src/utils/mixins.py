import pytest
import logging

from src.consts.input_values import VALUES


logger = logging.getLogger(__name__)


class VideocoinMixin:

    @pytest.fixture(autouse=True)
    def init_cluster(self, cluster):
        self.cluster = cluster

    def get_initial_value(self, variable):
        return VALUES[self.cluster][variable]
