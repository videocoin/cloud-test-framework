import subprocess
import os
import signal
from datetime import datetime

def start_rtmp_output(source, destination):
    bbb_vid = './small.mp4'

    if source == 'video':
        UNCONFIGURED_FFMPEG_ARGS = [ "ffmpeg",
            "-threads", "1",
            # Both -fflags +genpts and -stream_loop -1 are necessary to 
            # create a looped video
            "-fflags", "+genpts",
            "-stream_loop", "-1",
            # Read input at native frame rate
            "-re",
            # Input file
            "-i", bbb_vid,
            # Resolution
            "-s", "1280x720",
            # Specify video codec to transcode
            "-vcodec", "libx264",
            # Specify constant rate factor (Lower is better)
            "-crf", "24",
            # b:v, minrate, maxrate, and bufsize will help determine a more
            # constant bitrate. Otherwise, leave only crf on
            # "-b:v", "6M",
            # "-minrate", "1M",
            # "-maxrate", "1M",
            # "-bufsize", "2M",
            # Number of audio channels
            "-ac", "2",
            # Sampling frequency
            "-ar", "44100",
            # Specify audio codec (copy) to transcode
            "-c:a", "aac",
            # Target bitrate for audio
            "-b:a", "64k",
            # Output format
            "-f", "flv", destination]

    now = datetime.now()
    str_formatted_now = now.strftime('%Y-%m-%d-%H:%M:%S.%f')
    log_directory = './logs/{}'.format(str_formatted_now)
    os.makedirs(log_directory)
    with open(os.path.join(log_directory, 'ffmpeg_stdout.txt'), 'w+') as ffmpeg_stdout, \
    open (os.path.join(log_directory, 'ffmpeg_stderr.txt'), 'w+') as ffmpeg_stderr:
        proc = subprocess.Popen(UNCONFIGURED_FFMPEG_ARGS, stdout=ffmpeg_stdout, stderr=ffmpeg_stderr)

    return proc.pid

def stop_rtmp_output(pid, signal_to_send=signal.SIGTERM):
    return os.kill(pid, signal_to_send)
