import pytest


@pytest.mark.skip('still working on this')
def test_get_miners(user, rtmp_runner):
    stream = user.create_stream(profile_name='copy')
    for miner in user.get_miners():
        if miner.name == 'small-dew':
            miner.assign_stream(stream.id)

    stream.start()
    try:
        stream.wait_for_status('STREAM_STATUS_PREPARED')
        rtmp_runner.start(stream.rtmp_url)
        stream.wait_for_status('STREAM_STATUS_READY')
        stream.is_hls_playlist_healthy(120, 20)
    finally:
        stream.stop()
        stream.wait_for_status('STREAM_STATUS_COMPLETED')
        rtmp_runner.stop()
        # stream.delete()
