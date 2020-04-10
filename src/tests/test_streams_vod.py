import pytest
import logging
import time

from src.utils.mixins import VideocoinMixin
from src.models.stream import StreamFactory
from src.consts.input_values import RPC_NODE_URL, STREAM_MANAGER_CONTRACT_ADDR
from src.blockchain import Blockchain, ValidatorCollection

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

    @pytest.mark.functional
    def test_vod_stream_blockchain_events(self, user):
        """
        Validate blockchain events for vod stream
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
            time.sleep(10)
            blockchain = Blockchain(
                self.get_initial_value(RPC_NODE_URL),
                stream_id=new_stream.stream_contract_id,
                stream_address=new_stream.stream_contract_address,
                stream_manager_address=self.get_initial_value(STREAM_MANAGER_CONTRACT_ADDR),
            )

            events = blockchain.get_all_events()
            validator = ValidatorCollection(
                events=events,
                input_url=new_stream.input_url,
                output_url=new_stream.output_url
            )
            for k, v in validator.validate().items():
                assert v.get('is_valid'), '{}: {}'.format(k, ', '.join(v.get('errors')))

        finally:
            new_stream.delete()
