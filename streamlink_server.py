from flask import Flask, request, Response
import subprocess
import time
from typing import Dict, Optional

app = Flask(__name__)

# Maximum number of concurrent streams
MAX_STREAMS: int = 3

# Dictionary to track active stream processes
STREAMS: Dict[str, subprocess.Popen[bytes]] = {}

# Dictionary to track the last accessed timestamp of each stream
TS: Dict[str, float] = {}

def generate_streamlink_process(url: str) -> subprocess.Popen[bytes]:
    """
    Starts a Streamlink subprocess to fetch and stream video content.

    Args:
        url (str): The URL of the video stream.

    Returns:
        subprocess.Popen[bytes]: The subprocess running Streamlink.
    """
    return subprocess.Popen(
        [
            'streamlink',
            '--hls-live-restart',  # Restart stream on interruption
            '--retry-streams', '3',  # Number of retry attempts
            '--stream-timeout', '60',  # Timeout for fetching stream data
            '--hls-playlist-reload-attempts', '3',  # Retries for loading a new HLS playlist
            '--stdout', url, 'best'  # Output best-quality stream to stdout
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

@app.route('/stream')
def stream() -> Response:
    """
    Handles HTTP requests to start a video stream via Streamlink.

    Query Parameters:
        url (str): The URL of the video stream to fetch.

    Returns:
        Response: A streaming HTTP response containing the video data.
    """
    url: Optional[str] = request.args.get('url')
    if not url:
        return Response("No URL provided.", status=400)

    TS[url] = time.time()

    if url in STREAMS:
        current_stream = STREAMS[url]
    else:
        STREAMS[url] = current_stream = generate_streamlink_process(url)

    # NOTE:  when used in .m3u whenever we change "channel" a new process is launched that handles streaming in background
    # HACK: kill oldest stream if process list grows too much
    # this can and will cause issues for multi-user setups, works fine in my homelab
    if len(STREAMS) > MAX_STREAMS:
        oldest_url = min(TS, key=TS.get)
        app.logger.warning(f"Max concurrent streams reached, killing {oldest_url}")
        oldest_stream = STREAMS.pop(oldest_url)
        oldest_stream.terminate()
        TS.pop(oldest_url)

    def generate():
        """
        Generator function that yields stream data in chunks.
        Terminates the process if no more data is available.
        """
        nonlocal current_stream

        while True:
            output = current_stream.stdout.read(1024)
            if not output:
                current_stream.terminate()
                return
            yield output

    return Response(
        generate(),
        content_type='video/mp2t',  # MPEG-TS format
        direct_passthrough=True
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6090)
