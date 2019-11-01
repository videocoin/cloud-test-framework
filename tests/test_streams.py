import requests
import pytest
# import pdb
# from time import sleep

from consts import expected_results

def test_creating_valid_stream_appears_in_streams_list(user):
    try:
        new_stream = user.create_stream()
        all_streams = user.get_streams()
        found_stream = [stream for stream in all_streams 
            if stream.id == new_stream.id]
        assert len(found_stream) == 1
    # TODO: What if I created a "stream" fixture that would delete itself in fin()
    # But how do I associate that stream with the user fixture? What if I don't want
    # to delete the stream at the end of the test? Will I ever want that?
    finally:
        new_stream.delete()
        all_streams = user.get_streams()
        other_found_stream = [stream for stream in all_streams 
            if stream.id == new_stream.id]
        assert len(other_found_stream) == 0

# TODO: Need to change test to verify the format of these values, not just
# check that they're not None
def test_creating_valid_stream_has_correct_information(user):
    try:
        new_stream = user.create_stream()
        tested_keys = expected_results.NEW_STREAM_INFORMATION.keys()
        for key in tested_keys:
            assert new_stream.json()[key] is not None
    finally:
        new_stream.delete()
        all_streams = user.get_streams()
        other_found_stream = [stream for stream in all_streams 
            if stream.id == new_stream.id]
        assert len(other_found_stream) == 0

def test_creating_stream_with_empty_name_returns_error(user):
    with pytest.raises(requests.HTTPError) as e:
        user.create_stream(name='')
    assert e.value.response.status_code == 400
    assert e.value.response.json() == expected_results.CREATE_STREAM_WITH_EMPTY_NAME_ERROR

def test_creating_stream_with_empty_profile_id_returns_error(user):
    with pytest.raises(requests.HTTPError) as e:
        user.create_stream(profile_id='')
    assert e.value.response.status_code == 400
    assert e.value.response.json() == expected_results.CREATE_STREAM_WITH_EMPTY_PROFILE_ID_ERROR

@pytest.mark.skip(reason="What's the expected behavior of an invalid profile_id?")
def test_creating_stream_with_invalid_profile_id(user):
    with pytest.raises(requests.HTTPError) as e:
        user.create_stream(profile_id='abcd-1234')
    print(e)
