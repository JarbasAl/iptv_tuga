import re
import subprocess
import json

PREFIX = "http://192.168.1.200:6090/stream?url="


def get_live_streams(channel_url):
    command = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-json",
        channel_url
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    videos = [json.loads(line) for line in result.stdout.strip().split("\n") if line]

    return videos


def remove_emojis(text):
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]+",
        flags=re.UNICODE)
    return emoji_pattern.sub("", text)


M3U = ""

for url in [
    "https://www.youtube.com/@LofiGirl/streams",
    "https://www.youtube.com/@LofiontheRooftop/streams",
    "https://www.youtube.com/@FilipLackovicMusic/streams",
    "https://www.youtube.com/@celestialaeonproject/streams",
    "https://www.youtube.com/@Pluviophile_Lofi/streams",
    "https://www.youtube.com/@Aestheticlofi./streams",
    "https://www.youtube.com/@HealingWithMe./streams",
    "https://www.youtube.com/@TokyoTones/streams",
    "https://www.youtube.com/@ChillhopMusic/streams",
    "https://www.youtube.com/@InYourChill/streams",
    "https://www.youtube.com/@NightrideFM/streams",
    "https://www.youtube.com/@SpongeBobLofi/streams",
    "https://www.youtube.com/@futaba-cafe/streams",
    "https://www.youtube.com/@GlitchxCity/streams",
    "https://www.youtube.com/@LoFi_Pokemon_Matcha/streams",
    "https://www.youtube.com/@CinderyLofi/streams",
    "https://www.youtube.com/@FantasyLofi/streams",
    "https://www.youtube.com/@ChillAstronaut/streams",
    "https://www.youtube.com/@Frip2gameOrg/streams"

]:
    live_videos = get_live_streams(url)
    for video in live_videos:
        if video.get("duration"):  # not live
            continue
        # print(video)
        title = remove_emojis(video['title'])
        pic = video['thumbnails'][0]["url"]  # TODO channel thumbnail for logo
        stream = PREFIX + video['url']
        M3U += f"""\n#EXTINF:-1 group-title="TV"", {title}\n{stream}\n"""

with open("youtube_lofi.m3u", "w") as f:
    f.write(M3U)
