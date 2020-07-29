import pytest
import logging

from src.utils.mixins import VideocoinMixin
from src.models.miners import MinerFactory

logger = logging.getLogger(__name__)


class TestMiner(VideocoinMixin):

    @pytest.mark.smoke
    def test_get_all_miners(self):
        miners = MinerFactory(self.cluster)
        assert miners.all() is not None

    @pytest.mark.smoke
    def test_get_my_miners(self, user):
        miners = MinerFactory(self.cluster, user.token)
        assert miners.my() is not None
