import yt_dlp
import os
#  & C:\Users\dasre\Documents\Knowledge-db\.venv\Scripts\python.exe c:/Users/dasre/Documents/Knowledge-db/ghFiles/pycodes/videodownl/video.py


rolas = [
    "https://youtu.be/21YeWkTzCWk?si=30Om4XJSeizPrelY",
    "https://youtu.be/mVJdBfAXCfA?si=cjQnEw-FVwNI-qzS"
]

URL = "https://youtu.be/21YeWkTzCWk?si=30Om4XJSeizPrelY"
PATH = r"C:\Users\dasre\Documents\Knowledge-db"
artist = "Quantum"
DOWNLOAD_AUDIO_ONLY = True  # Set to False to download video

# Add ffmpeg to PATH
ffmpeg_path = r"C:\Users\dasre\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"
os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ["PATH"]

if DOWNLOAD_AUDIO_ONLY:
    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "outtmpl": f"{PATH}/%(title)s.%(ext)s",
        "noplaylist": False,
        "ignoreerrors": True,
        "no_warnings": True,
        "logger": None,
    }
else:
    ydl_opts = {
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "outtmpl": f"{PATH}/%(title)s.%(ext)s",
        "noplaylist": False,
        "ignoreerrors": True,
        "no_warnings": True,
        "logger": None,
    }

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    #ydl.download([URL])
    ydl.download(rolas)
