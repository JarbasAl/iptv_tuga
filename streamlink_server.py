from flask import Flask, request, Response
import subprocess

app = Flask(__name__)

def generate_streamlink_process(url):
    """
    Run Streamlink as a subprocess and pipe its output to the response.
    """
    process = subprocess.Popen(
        [
            'streamlink',
            '--hls-live-restart',  # Automatically restarts stream on interruption
            '--retry-streams', '3',  # Number of times to retry fetching the stream
            '--stream-timeout', '60',  # Timeout for fetching stream data
            '--hls-playlist-reload-attempts', '3',  # Number of retries for loading a new HLS playlist
            '--stdout', url, 'best'  # Output stream to stdout in the best quality available
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return process

@app.route('/stream')
def stream():
    url = request.args.get('url')
    if not url:
        return "No URL provided.", 400

    try:
        process = generate_streamlink_process(url)

        def generate():
            nonlocal process  # Declare 'process' as a nonlocal variable
            while True:
                output = process.stdout.read(1024)
                if not output:
                    # If no output, the process may have ended, attempt to restart it
                    process.terminate()
                    process = generate_streamlink_process(url)
                    continue
                yield output

        return Response(
            generate(),
            content_type='video/mp2t',  # Set content type based on the stream format
            direct_passthrough=True
        )
    except Exception as e:
        return f"Error starting Streamlink: {str(e)}", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6090)