import pytest
import logging
import time

from src.utils.mixins import VideocoinMixin
from src.models.stream import StreamFactory

logger = logging.getLogger(__name__)


class TestVodStreams(VideocoinMixin):

    @pytest.fixture(autouse=True)
    def create_stream_factory(self, cluster, user):
        self.stream_factory = StreamFactory(cluster, user.token)

    @pytest.mark.smoke
    @pytest.mark.functional
    def test_creating_valid_stream_appears_in_streams_list(self):
        """
        Create vod stream and check list response
        """
        try:
            new_stream = self.stream_factory.create_vod()
            logging.debug('New stream created: %s', new_stream.id)
            all_streams = self.stream_factory.my()
            found_stream = [stream for stream in all_streams if stream.id == new_stream.id]
            assert len(found_stream) == 1
        finally:
            new_stream.delete()
            all_streams = self.stream_factory.my()
            other_found_stream = [
                stream for stream in all_streams if stream.id == new_stream.id
            ]
            assert len(other_found_stream) == 0

    @pytest.mark.smoke
    @pytest.mark.functional
    def test_creating_stream_and_upload_file(self, user):
        """
        Check file upload via local file
        """
        try:
            self.faucet_vid_to_account(user.wallet_address, 11)
            new_stream = self.stream_factory.create_vod()
            time.sleep(5)
            new_stream.start()

            new_stream.wait_for_status('STREAM_STATUS_PREPARED')
            new_stream.upload_file('files/small.mp4')
            new_stream.wait_for_status('STREAM_STATUS_COMPLETED')
            assert new_stream.check_playlist()
        finally:
            new_stream.delete()

    @pytest.mark.smoke
    @pytest.mark.functional
    def test_creating_stream_and_upload_url(self, user):
        """
        Check file upload via url
        """
        try:
            self.faucet_vid_to_account(user.wallet_address, 11)
            new_stream = self.stream_factory.create_vod()
            time.sleep(5)
            new_stream.start()

            new_stream.wait_for_status('STREAM_STATUS_PREPARED')
            new_stream.upload_url('http://techslides.com/demos/sample-videos/small.mp4')
            new_stream.wait_for_status('STREAM_STATUS_COMPLETED')
            assert new_stream.check_playlist()
        finally:
            new_stream.delete()
