import requests
import pytest

from consts import expected_results

def test_creating_stream_with_empty_name_gives_error(user):
    sm = user.get_stream_manager()
    with pytest.raises(requests.HTTPError) as e:
        sm.create_stream(name='')
    assert e.value.response.status_code == 400
    assert e.value.response.json() == expected_results.CREATE_STREAM_WITH_EMPTY_NAME_ERROR

def test_creating_stream_with_empty_profile_id_gives_error(user):
    sm = user.get_stream_manager()
    with pytest.raises(requests.HTTPError) as e:
        sm.create_stream(profile_id='')
    assert e.value.response.status_code == 400
    assert e.value.response.json() == expected_results.CREATE_STREAM_WITH_EMPTY_PROFILE_ID_ERROR

@pytest.mark.skip(reason="What's the expected behavior of an invalid profile_id?")
def test_creating_stream_with_invalid_profile_id(user):
    sm = user.get_stream_manager()
    with pytest.raises(requests.HTTPError) as e:
        sm.create_stream(profile_id='abcd-1234')
    print(e)
