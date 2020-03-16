from time import sleep
import requests
import pytest
import logging

from src.consts import expected_results
from src.utils.mixins import VideocoinMixin

logger = logging.getLogger(__name__)


class TestLiveStreams(VideocoinMixin):

    @pytest.mark.smoke
    @pytest.mark.functional
    def test_creating_valid_stream_appears_in_streams_list(self, user):
        try:
            new_stream = user.create_stream_live()
            logging.debug('New stream created: %s', new_stream.id)
            all_streams = user.get_streams()
            found_stream = [stream for stream in all_streams if stream.id == new_stream.id]
            assert len(found_stream) == 1
        # TODO: What if I created a "stream" fixture that would delete itself in fin()
        # But how do I associate that stream with the user fixture? What if I don't want
        # to delete the stream at the end of the test? Will I ever want that?
        finally:
            new_stream.delete()
            all_streams = user.get_streams()
            other_found_stream = [
                stream for stream in all_streams if stream.id == new_stream.id
            ]
            assert len(other_found_stream) == 0

    @pytest.mark.smoke
    @pytest.mark.functional
    # TODO: Need to change test to verify the format of these values, not just
    # check that they're not None
    def test_creating_valid_stream_has_correct_information(self, user):
        try:
            new_stream = user.create_stream_live()
            tested_keys = expected_results.NEW_STREAM_INFORMATION.keys()
            for key in tested_keys:
                # These keys are expected to be None (or null)
                if key in ['ready_at', 'completed_at']:
                    assert new_stream.json()[key] is None
                else:
                    assert new_stream.json()[key] is not None
        finally:
            new_stream.delete()

    @pytest.mark.smoke
    @pytest.mark.functional
    def test_creating_stream_and_send_data_to_rtmp_url_starts_output_stream(self, user, rtmp_runner):
        try:
            if user.token_type == 'sign_in':
                self.faucet_vid_to_account(user.wallet_address, 11)
            new_stream = user.create_stream_live()
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
            new_stream = user.create_stream_live()
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
            new_stream = user.create_stream_live()
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
                new_stream = user.create_stream_live()
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
                new_stream = user.create_stream_live()
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
                new_stream = user.create_stream_live()
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
            user.create_stream_live(name='')
        assert e.value.response.status_code == 400
        assert (
            e.value.response.json() == expected_results.CREATE_STREAM_WITH_EMPTY_NAME_ERROR
        )

    @pytest.mark.functional
    def test_creating_stream_with_empty_profile_id_returns_error(self, user):
        with pytest.raises(requests.HTTPError) as e:
            user.create_stream_live(profile_id='')
        assert e.value.response.status_code == 400
        assert (
            e.value.response.json()
            == expected_results.CREATE_STREAM_WITH_EMPTY_PROFILE_ID_ERROR
        )

    @pytest.mark.functional
    def test_creating_stream_with_invalid_profile_id(self, user):
        with pytest.raises(requests.HTTPError) as e:
            user.create_stream_live(profile_id='abcd-1234')
        assert e.value.response.status_code == 400

    # Parametrized with all available profiles picked up at run time. See
    # pytest_generate_tests in conftest.py
    def test_all_available_output_profiles(self, user, rtmp_runner, output_profile):
        logger.debug('running with profile name: {}'.format(output_profile['name']))
        profile_id = output_profile['id']
        new_stream = user.create_stream_live(profile_id=profile_id)
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

    def test_playlist_size(self, user, rtmp_runner):
        start_balance = user.wallet_balance
        new_stream = user.create_stream_live()
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
