import pytest
import logging
import time

from src.utils.mixins import VideocoinMixin
from src.models.stream import StreamFactory
from src.consts.input_values import RPC_NODE_URL, STREAM_MANAGER_CONTRACT_ADDR
from src.blockchain import Blockchain, ValidatorCollection

logger = logging.getLogger(__name__)


class TestRTCStreams(VideocoinMixin):

    @pytest.fixture(autouse=True)
    def create_stream_factory(self, cluster, user):
        self.stream_factory = StreamFactory(cluster, user.token)

    # @pytest.mark.smoke
    # @pytest.mark.functional
    # def test_webrtc_stream(self):
    #     """
    #     Create vod stream and check list response
    #     """
    #     try:
    #         new_stream = self.stream_factory.create_rtc()
    #         logging.debug('New stream created: %s', new_stream.id)
    #         all_streams = self.stream_factory.my()
    #         found_stream = [stream for stream in all_streams if stream.id == new_stream.id]
    #         assert len(found_stream) == 1
    #     finally:
    #         new_stream.delete()
    #         all_streams = self.stream_factory.my()
    #         other_found_stream = [
    #             stream for stream in all_streams if stream.id == new_stream.id
    #         ]
    #         assert len(other_found_stream) == 0

    @pytest.mark.smoke
    @pytest.mark.functional
    def test_webrtc_stream(self, rtmp_runner):
        """
        Check rtc stream run and playlist health
        """
        # print(rtmp_runner.start_rtc(stream_id='8e70a47c-f8fd-466f-584f-c2276fe990c8',
        #                             cluster='https://studio.dev.videocoin.network/api/v1'))
        # exit()
        try:
            new_stream = self.stream_factory.create_rtc()

            time.sleep(5)
            rtmp_runner.start_rtc(stream_id=new_stream.id, cluster='https://console.dev.videocoin.network/api/v1')

            new_stream.start()
            time.sleep(240)
            # assert new_stream.check_playlist()
            new_stream.wait_for_status('STREAM_STATUS_PREPARED')

            new_stream.wait_for_status('STREAM_STATUS_READY')
            # assert new_stream.is_hls_playlist_healthy(120)
        finally:
            new_stream.stop()
            new_stream.wait_for_status('STREAM_STATUS_COMPLETED')
            rtmp_runner.stop()
            new_stream.delete()
