import pytest
import logging

from src.utils import utils

logger = logging.getLogger(__name__)


@pytest.mark.smoke
@pytest.mark.functional
def test_creating_valid_stream_appears_in_streams_list(user):
    """
    Create vod stream and check list response
    """
    try:
        new_stream = user.create_stream_vod()
        logging.debug('New stream created: %s', new_stream.id)
        all_streams = user.get_streams()
        found_stream = [stream for stream in all_streams if stream.id == new_stream.id]
        assert len(found_stream) == 1
    finally:
        new_stream.delete()
        all_streams = user.get_streams()
        other_found_stream = [
            stream for stream in all_streams if stream.id == new_stream.id
        ]
        assert len(other_found_stream) == 0


@pytest.mark.smoke
@pytest.mark.functional
def test_creating_stream_and_upload_file(user):
    """
    Check file upload via local file
    """
    try:
        if user.token_type == 'sign_in':
            utils.faucet_vid_to_account(user.wallet_address, 11)
        new_stream = user.create_stream_vod()
        new_stream.start()

        new_stream.wait_for_status('STREAM_STATUS_PREPARED')
        new_stream.upload_file('files/small.mp4')
        new_stream.wait_for_status('STREAM_STATUS_COMPLETED')
        assert new_stream.check_playlist()
    finally:
        new_stream.delete()


@pytest.mark.smoke
@pytest.mark.functional
def test_creating_stream_and_upload_url(user):
    """
    Check file upload via url
    """
    try:
        if user.token_type == 'sign_in':
            utils.faucet_vid_to_account(user.wallet_address, 11)
        new_stream = user.create_stream_vod()
        new_stream.start()

        new_stream.wait_for_status('STREAM_STATUS_PREPARED')
        new_stream.upload_url('http://techslides.com/demos/sample-videos/small.mp4')
        new_stream.wait_for_status('STREAM_STATUS_COMPLETED')
        assert new_stream.check_playlist()
    finally:
        new_stream.delete()
