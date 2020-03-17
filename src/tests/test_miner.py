import pytest
import logging

from src.utils.mixins import VideocoinMixin
from src.models.miner import MinerList

logger = logging.getLogger(__name__)


class TestMiner(VideocoinMixin):

    @pytest.mark.smoke
    def test_get_all_miners(self):
        miners = MinerList(self.cluster)
        assert miners.all() is not None

    @pytest.mark.smoke
    def test_get_my_miners(self, user):
        miners = MinerList(self.cluster, user.token)
        assert miners.my() is not None

    @pytest.mark.skip('still working on this')
    def test_get_miners(self, user, rtmp_runner):
        stream = user.create_stream_live(profile_name='copy')
        for miner in user.get_miners():
            if miner.name == 'small-dew':
                miner.assign_stream(stream.id)

        stream.start()
        try:
            stream.wait_for_status('STREAM_STATUS_PREPARED')
            rtmp_runner.start(stream.rtmp_url)
            stream.wait_for_status('STREAM_STATUS_READY')
            stream.is_hls_playlist_healthy(120, 20)
        finally:
            stream.stop()
            stream.wait_for_status('STREAM_STATUS_COMPLETED')
            rtmp_runner.stop()
            # stream.delete()
