from time import sleep
from datetime import datetime
import requests
import pytest
import logging

from consts import expected_results
from utils import utils

logger = logging.getLogger(__name__)


@pytest.mark.smoke
@pytest.mark.functional
def test_creating_valid_stream_appears_in_streams_list(user):
    """
    Name:
    Creating valid stream appears in streams list

    Description:
    When the user creates a new stream, the new stream should appear when calling the list
    streams API. This validates the list stream API is updated immediately after new stream
    creation.

    Steps:
    0. Create new stream with valid name and profile
    0. Verify the newly created stream is added and shown in the list of streams
    0. Delete the newly created stream to return account back to state before test

    Expected results:
    0. New stream is created and can be found in list of streams
    0. Removing the stream restores the list back to its original state
    """
    try:
        new_stream = user.create_stream()
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
def test_creating_valid_stream_has_correct_information(user):
    """
    Name:
    Creating valid stream has correct information

    Description:
    When the user creates a new stream, the stream should have the correct fields and
    correct values (if they're available).

    Steps:
    0. Create new stream with valid name and profile
    0. Verify newly created stream's information

    Expected results:
    0. All expected fields appear in stream object
    0. All fields that are expected to be filled have correct information
    """
    try:
        new_stream = user.create_stream()
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
def test_creating_stream_and_send_data_to_rtmp_url_starts_output_stream(
    user, rtmp_runner
):
    """
    Name:
    Creating stream and sending data to RTMP URL starts output stream

    Description:
    When the user creates a stream and begins sending data to its RTMP URL, the stream
    should begin transcoding the data and provide output to its output URL.

    Steps:
    0. Create new stream with valid name and profile and note its RTMP URL
    0. Start preparing the stream and wait for it to be prepared
    0. Begin streaming to the stream's RTMP URL and wait for output stream to be ready
    0. Allow stream to run for 60 seconds

    Expected results:
    0. Streaming to stream's RTMP URL creates valid content in stream's output URL
    0. Stream from output HLS stream can be viewed properly
    """
    try:
        if user.token_type == 'sign_in':
            utils.faucet_vid_to_account(user.wallet_address, 11)
        new_stream = user.create_stream()
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
def test_cancelling_stream_after_input_url_ready_cancels_stream(user):
    try:
        utils.faucet_vid_to_account(user.wallet_address, 11)
        new_stream = user.create_stream()
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
def test_cancelling_stream_during_input_processing_cancels_stream(user, rtmp_runner):
    try:
        # utils.faucet_vid_to_account(user.wallet_address, 11)
        new_stream = user.create_stream()
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
def test_time_it_takes_for_stream_prepared_state_is_less_than_expected_time(user):
    """
    Name:
    Time it takes for stream to reach prepared state is less than expected time

    Description:
    When the user starts preparing a stream (clicking "Start stream"), the time it takes
    for the stream to prepare the input and RTMP URLs should be less than a benchmarked
    amount of time. This is used to make sure time to prepare the streams have not regressed

    Steps:
    0. Create new stream with valid name and profile
    0. Start preparing the stream and begin timing its duration
    0. Once stream is prepared (input and RTMP URLs are preapred), stop timer
    0. Average time across 5 tests

    Expected results:
    0. Time to successfully prepare stream is less than benchmarked time over average of 5 tests
    """
    NUM_OF_TESTS = 5
    EXPECTED_TIME = 10

    results = []
    for i in range(NUM_OF_TESTS):
        try:
            utils.faucet_vid_to_account(user.wallet_address, 11)
            new_stream = user.create_stream()
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
    user, rtmp_runner
):
    """
    Name:
    Time it takes for stream to reach prepared state is less than expected time

    Description:
    After a stream has been prepared, (input and RTMP URLs are ready), the time it takes
    for the stream to transcode and output the HLS stream from an endcoder should be less
    than a benchmarked amount of time. This is used to make sure the time it takes for
    output to be ready have not regressed

    Steps:
    0. Create new stream with valid name and profile
    0. Start preparing the stream
    0. Once stream is prepared, begin sending stream data from encoder and start timing
    0. When output is ready, stop timer
    0. Average time across 5 tests

    Expected results:
    0. Time to successfully prepare ouput is less than benchmarked time over average of 5 tests
    """
    NUM_OF_TESTS = 5
    EXPECTED_TIME = 120

    results = []
    for i in range(NUM_OF_TESTS):
        try:
            utils.faucet_vid_to_account(user.wallet_address, 11)
            new_stream = user.create_stream()
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
    user, rtmp_runner
):
    """
    Name:
    Time it takes for stream to reach completed state is less than expected time

    Description:
    After a stream has successfully transcoded its input and is finished, the time it
    takes for the stream to complete after user initiation should be less than a
    benchmarked amount of time. This is used to make sure the time it takes for stream
    to be completed have not regressed

    Steps:
    0. Create new stream with valid name and profile
    0. Start preparing the stream
    0. Once stream is prepared, begin sending stream data from encoder
    0. Allow stream to transcode for a short while
    0. Initiate stream completion and start timer
    0. Wait for stream to successfully transition to completed state and stop timer
    0. Average time across 5 tests

    Expected results:
    0. Time to successfully complete is less than benchmarked time over average of 5 tests
    """
    NUM_OF_TESTS = 5
    EXPECTED_TIME = 5

    results = []
    for i in range(NUM_OF_TESTS):
        try:
            utils.faucet_vid_to_account(user.wallet_address, 11)
            new_stream = user.create_stream()
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
def test_creating_stream_with_empty_name_returns_error(user):
    """
    Name:
    Creating stream with empty name returns error

    Description:
    Users who attempt to create a new stream with an empty name field should be given
    an error. Name is a required field for stream creation.

    Steps:
    0. Create new stream with empty name field and valid profile

    Expected results:
    0. Server returns error with message name is a required field
    """
    with pytest.raises(requests.HTTPError) as e:
        user.create_stream(name='')
    assert e.value.response.status_code == 400
    assert (
        e.value.response.json() == expected_results.CREATE_STREAM_WITH_EMPTY_NAME_ERROR
    )


@pytest.mark.functional
def test_creating_stream_with_empty_profile_id_returns_error(user):
    """
    Name:
    Creating stream with empty profile ID returns error

    Description:
    Users who attempt to create a new stream with an empty profile ID field should be
    given an error. Profile ID is a required field for stream creation.

    Steps:
    0. Create new stream with valid name and empty profile ID

    Expected results:
    0. Server returns error with message profile ID is a required field
    """
    with pytest.raises(requests.HTTPError) as e:
        user.create_stream(profile_id='')
    assert e.value.response.status_code == 400
    assert (
        e.value.response.json()
        == expected_results.CREATE_STREAM_WITH_EMPTY_PROFILE_ID_ERROR
    )


@pytest.mark.functional
def test_creating_stream_with_invalid_profile_id(user):
    """
    Name:
    Creating stream with invalid profile ID returns error

    Description:
    Users who attempt to create a new stream with an invalid profile ID (not listed under
    the /profiles endpoint) should return an error. Users are forced to use the
    predetrmined transcoding profiles

    Steps:
    0. Create new stream with valid name and invalid profile ID

    Expected results:
    0. Server returns error with message a valid profile ID is requried
    """
    with pytest.raises(requests.HTTPError) as e:
        user.create_stream(profile_id='abcd-1234')
    assert e.value.response.status_code == 400


# Parametrized with all available profiles picked up at run time. See
# pytest_generate_tests in conftest.py
def test_all_available_output_profiles(user, rtmp_runner, output_profile):
    logger.debug('running with profile name: {}'.format(output_profile['name']))
    profile_id = output_profile['id']
    new_stream = user.create_stream(profile_id=profile_id)
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


def test_playlist_size(user, rtmp_runner):
    start_balance = user.wallet_balance
    new_stream = user.create_stream()
    new_stream.start()
    new_stream.wait_for_status('STREAM_STATUS_PREPARED')
    rtmp_runner.start(new_stream.rtmp_url)
    new_stream.wait_for_status('STREAM_STATUS_READY')
    new_stream.wait_for_playlist_size(10)
    new_stream.stop()
    sleep(120)
    end_balance = user.wallet_balance

    logger.debug('Start balance: {:.6e}'.format(start_balance))
    logger.debug('End balance: {:.6e}'.format(end_balance))
    logger.debug('Balance difference: {:.6e}'.format(start_balance - end_balance))
