from time import sleep
import requests
import pytest
import time
import logging

from src.consts import expected_results
from src.utils.mixins import VideocoinMixin
from src.models.stream import StreamFactory
from src.consts.input_values import RPC_NODE_URL, STREAM_MANAGER_CONTRACT_ADDR
from src.blockchain import Blockchain, ValidatorCollection

logger = logging.getLogger(__name__)


class TestLiveStreams(VideocoinMixin):

    @pytest.fixture(autouse=True)
    def create_stream_factory(self, cluster, user):
        self.stream_factory = StreamFactory(cluster, user.token)

    @pytest.mark.smoke
    @pytest.mark.functional
    def test_creating_valid_stream_appears_in_streams_list(self):
        try:
            new_stream = self.stream_factory.create_live()
            logging.debug('New stream created: %s', new_stream.id)
            all_streams = self.stream_factory.my()
            found_stream = [stream for stream in all_streams if stream.id == new_stream.id]
            assert len(found_stream) == 1
        # TODO: What if I created a "stream" fixture that would delete itself in fin()
        # But how do I associate that stream with the user fixture? What if I don't want
        # to delete the stream at the end of the test? Will I ever want that?
        finally:
            new_stream.delete()
            all_streams = self.stream_factory.my()
            other_found_stream = [
                stream for stream in all_streams if stream.id == new_stream.id
            ]
            assert len(other_found_stream) == 0

    @pytest.mark.smoke
    @pytest.mark.functional
    def test_creating_stream_and_send_data_to_rtmp_url_starts_output_stream(self, user, rtmp_runner):
        try:
            self.faucet_vid_to_account(user.wallet_address, 11)
            new_stream = self.stream_factory.create_live()
            new_stream.start()

            new_stream.wait_for_status('STREAM_STATUS_PREPARED')
            rtmp_runner.start(new_stream.rtmp_url)
            new_stream.wait_for_status('STREAM_STATUS_READY')
            assert new_stream.is_hls_playlist_healthy(120)
        finally:
            new_stream.stop()
            new_stream.wait_for_status('STREAM_STATUS_COMPLETED')
            rtmp_runner.stop()
            new_stream.delete()

    @pytest.mark.functional
    def test_cancelling_stream_after_input_url_ready_cancels_stream(self, user):
        try:
            self.faucet_vid_to_account(user.wallet_address, 11)
            new_stream = self.stream_factory.create_live()
            new_stream.start()

            new_stream.wait_for_status('STREAM_STATUS_PREPARED')
            new_stream.stop()
            # Make sure it really stopped by waiting a little after invoking cancel
            sleep(5)
            new_stream.wait_for_status('STREAM_STATUS_COMPLETED')
        finally:
            new_stream.delete()
            pass

    @pytest.mark.functional
    def test_cancelling_stream_during_input_processing_cancels_stream(self, user, rtmp_runner):
        try:
            # utils.faucet_vid_to_account(user.wallet_address, 11)
            new_stream = self.stream_factory.create_live()
            new_stream.start()
            new_stream.wait_for_status('STREAM_STATUS_PREPARED')
            rtmp_runner.start(new_stream.rtmp_url)
            # Let stream run before attemtping to stop
            sleep(10)
            new_stream.stop()
            # Make sure it really stopped by waiting a little after invoking cancel
            sleep(5)
            new_stream.wait_for_status('STREAM_STATUS_COMPLETED')
        finally:
            new_stream.delete()

    @pytest.mark.performance
    def test_time_it_takes_for_stream_prepared_state_is_less_than_expected_time(self, user):
        NUM_OF_TESTS = 5
        EXPECTED_TIME = 10

        results = []
        for i in range(NUM_OF_TESTS):
            try:
                self.faucet_vid_to_account(user.wallet_address, 11)
                new_stream = self.stream_factory.create_live()
                new_stream.start()
                duration = new_stream.wait_for_status(
                    'STREAM_STATUS_PREPARED', timeout=EXPECTED_TIME
                )
                results.append(duration)
            finally:
                new_stream.stop()
                # TODO: Should this be CANCELLED or COMPLETED?
                new_stream.wait_for_status('STREAM_STATUS_COMPLETED')
                new_stream.delete()

        average = sum(results) / len(results)
        logger.info(
            'Average time to get stream prepared over {} tests: {}'.format(
                NUM_OF_TESTS, average
            )
        )
        assert average <= EXPECTED_TIME

    @pytest.mark.performance
    def test_time_it_takes_for_stream_to_reach_output_ready_state_is_less_than_expected_time(
        self, user, rtmp_runner
    ):
        NUM_OF_TESTS = 5
        EXPECTED_TIME = 120

        results = []
        for i in range(NUM_OF_TESTS):
            try:
                self.faucet_vid_to_account(user.wallet_address, 11)
                new_stream = self.stream_factory.create_live()
                new_stream.start()
                new_stream.wait_for_status('STREAM_STATUS_PREPARED')
                rtmp_runner.start(new_stream.rtmp_url)
                duration = new_stream.wait_for_status(
                    'STREAM_STATUS_READY', timeout=EXPECTED_TIME
                )
                results.append(duration)
            finally:
                new_stream.stop()
                new_stream.wait_for_status('STREAM_STATUS_COMPLETED')
                rtmp_runner.stop()
                new_stream.delete()

        average = sum(results) / len(results)
        logger.info(
            'Average time to get stream output ready over {} tests: {}'.format(
                NUM_OF_TESTS, average
            )
        )
        assert average <= EXPECTED_TIME

    # TODO: Something's not right about this test...
    # Is the transition to STREAM_STATUS_COMPLETED really instant?
    @pytest.mark.performance
    def test_time_it_takes_for_stream_to_reach_completed_state_is_less_than_expected_time(
        self, user, rtmp_runner
    ):
        NUM_OF_TESTS = 5
        EXPECTED_TIME = 5

        results = []
        for i in range(NUM_OF_TESTS):
            try:
                self.faucet_vid_to_account(user.wallet_address, 11)
                new_stream = self.stream_factory.create_live()
                new_stream.start()
                new_stream.wait_for_status('STREAM_STATUS_PREPARED')
                rtmp_runner.start(new_stream.rtmp_url)
                new_stream.wait_for_status('STREAM_STATUS_READY')
                new_stream.stop()
                duration = new_stream.wait_for_status(
                    'STREAM_STATUS_COMPLETED', timeout=EXPECTED_TIME
                )
                results.append(duration)
            finally:
                rtmp_runner.stop()
                new_stream.delete()

        average = sum(results) / len(results)
        logger.info(
            'Average time to get stream complete over {} tests: {}'.format(
                NUM_OF_TESTS, average
            )
        )
        assert average <= EXPECTED_TIME

    @pytest.mark.functional
    def test_creating_stream_with_empty_name_returns_error(self, user):
        with pytest.raises(requests.HTTPError) as e:
            self.stream_factory.create_live(name='')
        assert e.value.response.status_code == 400
        assert (
            e.value.response.json() == expected_results.CREATE_STREAM_WITH_EMPTY_NAME_ERROR
        )

    @pytest.mark.functional
    def test_creating_stream_with_empty_profile_id_returns_error(self, user):
        with pytest.raises(requests.HTTPError) as e:
            self.stream_factory.create_live(profile_id='')
        assert e.value.response.status_code == 400
        assert (
            e.value.response.json()
            == expected_results.CREATE_STREAM_WITH_EMPTY_PROFILE_ID_ERROR
        )

    @pytest.mark.functional
    def test_creating_stream_with_invalid_profile_id(self, user):
        with pytest.raises(requests.HTTPError) as e:
            self.stream_factory.create_live(profile_id='abcd-1234')
        assert e.value.response.status_code == 400

    # Parametrized with all available profiles picked up at run time. See
    # pytest_generate_tests in conftest.py
    @pytest.mark.functional
    def test_all_available_output_profiles(self, user, rtmp_runner, output_profile):
        logger.debug('running with profile name: {}'.format(output_profile['name']))
        profile_id = output_profile['id']
        new_stream = self.stream_factory.create_live(profile_id=profile_id)
        new_stream.start()
        try:
            new_stream.wait_for_status('STREAM_STATUS_PREPARED')
            rtmp_runner.start(new_stream.rtmp_url)
            new_stream.wait_for_status('STREAM_STATUS_READY')
            assert new_stream.is_hls_playlist_healthy(120)
        finally:
            new_stream.stop()
            new_stream.wait_for_status('STREAM_STATUS_COMPLETED')
            rtmp_runner.stop()
            new_stream.delete()

    @pytest.mark.functional
    def test_playlist_size(self, user, rtmp_runner):
        start_balance = user.wallet_balance
        new_stream = self.stream_factory.create_live()
        new_stream.start()
        try:
            new_stream.wait_for_status('STREAM_STATUS_PREPARED')
            rtmp_runner.start(new_stream.rtmp_url)
            new_stream.wait_for_status('STREAM_STATUS_READY')
            new_stream.wait_for_playlist_size(10)
        finally:
            new_stream.stop()
            new_stream.wait_for_status('STREAM_STATUS_COMPLETED')
            rtmp_runner.stop()
            new_stream.delete()

        sleep(120)
        end_balance = user.wallet_balance

        logger.debug('Start balance: {:.6e}'.format(start_balance))
        logger.debug('End balance: {:.6e}'.format(end_balance))
        logger.debug('Balance difference: {:.6e}'.format(start_balance - end_balance))

    @pytest.mark.functional
    def test_live_stream_blockchain_events(self, user, rtmp_runner):
        """
        Validate blockchain events for live stream
        """
        new_stream = self.stream_factory.create_live()
        new_stream.start()
        try:
            new_stream.wait_for_status('STREAM_STATUS_PREPARED')
            rtmp_runner.start(new_stream.rtmp_url)
            new_stream.wait_for_status('STREAM_STATUS_READY')
            new_stream.wait_for_playlist_size(10, 30)
            new_stream.stop()
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
