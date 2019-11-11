from time import sleep
from datetime import datetime
import requests
import pytest
import logging
import m3u8

from consts import expected_results
from utils.rtmp_runner import RTMPRunner

logger = logging.getLogger(__name__)


@pytest.mark.smoke
@pytest.mark.functional
def test_creating_valid_stream_appears_in_streams_list(user):
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
def test_creating_stream_and_send_data_to_rtmp_url(user):
    try:
        new_stream = user.create_stream()
        new_stream.start()

        _wait_for_stream_status(new_stream, 'STREAM_STATUS_PREPARED')
        rtmp_job = RTMPRunner('http://127.0.0.1:8000', new_stream.rtmp_url)
        rtmp_job.start()
        _wait_for_stream_status(new_stream, 'STREAM_STATUS_READY')
        # m3u8.load('https://streams-snb.videocoin.network/' + new_stream.id + '/index.m3u8')
        # Let 'er run
        sleep(60)
    finally:
        new_stream.stop()
        _wait_for_stream_status(new_stream, 'STREAM_STATUS_COMPLETED')
        rtmp_job.stop()
        new_stream.delete()


@pytest.mark.performance
def test_time_it_takes_for_stream_prepared(user):
    NUM_OF_TESTS = 5
    EXPECTED_TIME = 8

    results = []
    for i in range(NUM_OF_TESTS):
        try:
            new_stream = user.create_stream()
            new_stream.start()
            duration = _wait_for_stream_status(
                new_stream, 'STREAM_STATUS_PREPARED', timeout=EXPECTED_TIME
            )
            results.append(duration)
        finally:
            new_stream.stop()
            # TODO: Should this be CANCELLED or COMPLETED?
            _wait_for_stream_status(new_stream, 'STREAM_STATUS_COMPLETED')
            new_stream.delete()

    average = sum(results) / len(results)
    logger.info(
        'Average time to get stream prepared over {} tests: {}'.format(
            NUM_OF_TESTS, average
        )
    )
    assert average < EXPECTED_TIME


@pytest.mark.performance
def test_time_it_takes_for_stream_output_ready(user):
    NUM_OF_TESTS = 5
    EXPECTED_TIME = 35

    results = []
    for i in range(NUM_OF_TESTS):
        try:
            new_stream = user.create_stream()
            new_stream.start()
            _wait_for_stream_status(new_stream, 'STREAM_STATUS_PREPARED')
            rtmp_job = RTMPRunner('http://127.0.0.1:8000', new_stream.rtmp_url)
            rtmp_job.start()
            duration = _wait_for_stream_status(
                new_stream, 'STREAM_STATUS_READY', timeout=EXPECTED_TIME
            )
            results.append(duration)
        finally:
            new_stream.stop()
            _wait_for_stream_status(new_stream, 'STREAM_STATUS_COMPLETED')
            rtmp_job.stop()
            new_stream.delete()

    average = sum(results) / len(results)
    logger.info(
        'Average time to get stream output ready over {} tests: {}'.format(
            NUM_OF_TESTS, average
        )
    )
    assert average < EXPECTED_TIME


# TODO: Something's not right about this test...
# Is the transition to STREAM_STATUS_COMPLETED really instant?
@pytest.mark.performance
def test_time_it_takes_for_stream_complete(user):
    NUM_OF_TESTS = 5
    EXPECTED_TIME = 5

    results = []
    for i in range(NUM_OF_TESTS):
        try:
            new_stream = user.create_stream()
            new_stream.start()
            _wait_for_stream_status(new_stream, 'STREAM_STATUS_PREPARED')
            rtmp_job = RTMPRunner('http://127.0.0.1:8000', new_stream.rtmp_url)
            rtmp_job.start()
            _wait_for_stream_status(new_stream, 'STREAM_STATUS_READY')
            new_stream.stop()
            duration = _wait_for_stream_status(
                new_stream, 'STREAM_STATUS_COMPLETED', timeout=EXPECTED_TIME
            )
            results.append(duration)
        finally:
            rtmp_job.stop()
            new_stream.delete()

    average = sum(results) / len(results)
    logger.info(
        'Average time to get stream complete over {} tests: {}'.format(
            NUM_OF_TESTS, average
        )
    )
    assert average < EXPECTED_TIME


@pytest.mark.functional
def test_creating_stream_with_empty_name_returns_error(user):
    with pytest.raises(requests.HTTPError) as e:
        user.create_stream(name='')
    assert e.value.response.status_code == 400
    assert (
        e.value.response.json() == expected_results.CREATE_STREAM_WITH_EMPTY_NAME_ERROR
    )


@pytest.mark.functional
def test_creating_stream_with_empty_profile_id_returns_error(user):
    with pytest.raises(requests.HTTPError) as e:
        user.create_stream(profile_id='')
    assert e.value.response.status_code == 400
    assert (
        e.value.response.json()
        == expected_results.CREATE_STREAM_WITH_EMPTY_PROFILE_ID_ERROR
    )


@pytest.mark.functional
@pytest.mark.skip(reason="What's the expected behavior of an invalid profile_id?")
def test_creating_stream_with_invalid_profile_id(user):
    with pytest.raises(requests.HTTPError) as e:
        user.create_stream(profile_id='abcd-1234')
    print(e)


def _wait_for_stream_status(stream, status, timeout=60):
    start = datetime.now()
    while stream.status != status and _time_from_start(start) < timeout:
        sleep(1)
    if _time_from_start(start) > timeout:
        raise RuntimeError(
            'Stream {} took too long to transition to {}.'
            'Time allowed: {}. Status during failure: {}'.format(
                stream.id, status, timeout, stream.status
            )
        )

    return _time_from_start(start)


def _time_from_start(start):
    now = datetime.now()
    return (now - start).seconds
