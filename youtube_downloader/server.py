from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
from pytube import YouTube
from pathlib import Path
import shutil
import ffmpeg

app = FastAPI()

yt = None
download_folder = Path("tmp/")
download_folder.mkdir(parents=True, exist_ok=True)


class Payload(BaseModel):
    url: str = None


class Stream(BaseModel):
    type: str = None
    mime_type: str = None
    res: str = None
    bitrate: str = None
    fps: str = None
    video_codec: str = None
    audio_codec: str = None
    title: str = Field(default=None, required=True)
    itag: str = Field(default=None, required=True)
    progressive: bool = False


@app.post("/list_streams", response_model=List[Stream], status_code=200)
def list_streams(payload: Payload):
    global yt
    yt = YouTube(payload.url)

    streams = []
    for stream in yt.streams:
        streams += [Stream(
            type=stream.type,
            mime_type=stream.mime_type,
            res=stream.resolution,
            bitrate=stream.abr,
            fps=stream.fps,
            video_codec=stream.video_codec,
            audio_codec=stream.audio_codec,
            progressive=stream.is_progressive,
            title=yt.title,
            itag=stream.itag
        )]

    return streams


@app.post("/download", response_model=str, status_code=200)
def download(stream: Stream, _format: str = None):
    global yt

    if yt:
        ys = yt.streams.get_by_itag(stream.itag)
        file_path = ys.download(
            output_path=download_folder,
            filename=stream.title,
        )

        # Convert to desired format
        if _format:
            try:
                ffmpeg_file = ffmpeg.input(file_path)
                audio = ffmpeg_file.audio
                file_path = ''.join(file_path.split('.')[:-1]) + "." + _format
                out_file = ffmpeg.output(audio, file_path)
                out_file.run()
            except Exception as e:
                print(e)

        return file_path
    return None


@app.on_event("shutdown")
def shutdown():
    shutil.rmtree(download_folder)
