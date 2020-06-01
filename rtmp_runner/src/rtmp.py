import argparse
import logging
import os
import requests
import asyncio


logger = logging.getLogger(__name__)

logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))

from aiortc import (
    RTCIceCandidate,
    RTCPeerConnection,
    RTCSessionDescription,
    VideoStreamTrack,
)
from aiortc.contrib.media import MediaPlayer


def startWebRTC(stream_id, sdp, cluster):
    url = '{}/ms/streams/webrtc'.format(cluster)
    r = requests.post(url, json={'stream_id': stream_id, 'sdp': sdp})
    return r.json().get('sdp')


async def publish(pc, player, stream_id, cluster):

    @pc.on("track")
    def on_track(track):
        logger.warning("Track %s received" % track.kind)

    @pc.on("signalingstatechange")
    def on_signalingstatechange():
        logger.warning("signalingstatechange %s", pc._RTCPeerConnection__signalingState)

    @pc.on("iceconnectionstatechange")
    def on_iceconnectionstatechange():
        logger.warning("iceconnectionstatechange %s",  pc.iceConnectionState)

    @pc.on("icegatheringstatechange")
    def on_icegatheringstatechange():
        logger.warning("icegatheringstatechange %s",  pc.iceGatheringState)

    @pc.on("open")
    def on_open():
        logger.warning("open")

    pc.addTrack(player.audio)
    pc.addTrack(player.video)

    await pc.setLocalDescription(await pc.createOffer())
    sdp = startWebRTC(stream_id, pc.localDescription.sdp, cluster)
    await pc.setRemoteDescription(
        RTCSessionDescription(
            sdp=sdp, type='answer'
        )
    )


async def run(player, stream_id, cluster):

    pc = RTCPeerConnection()
    await publish(pc, player, stream_id, cluster)
    logger.warning("Exchanging media")
    await asyncio.sleep(600)


def start_rtc_output():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--stream_id", help="stream id"),
    parser.add_argument("--cluster", help="cluster api url"),
    args = parser.parse_args()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    vid_file = './small.mp4'
    player = MediaPlayer(vid_file)

    loop.run_until_complete(run(player, args.stream_id, args.cluster))

start_rtc_output()