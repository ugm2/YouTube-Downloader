from fastapi import FastAPI
from pydantic import BaseModel, validator
from typing import List
from pytube import YouTube

app = FastAPI()

allowed_formats = ['mp3']

class Payload(BaseModel):
    url: str = None
    download_format: str = 'mp3'

    @validator('download_format')
    def download_format_must_be_allowed(cls, v):
        if v not in allowed_formats:
            raise ValueError(f'must be one of these formats: {allowed_formats}')
        return v

class Stream(BaseModel):
    type: str = None
    format: str = None
    quality: str = None
    fps: str = None
    codec: str = None

@app.post("/list_streams", response_model=List[Stream], status_code=200)
def list_streams(payload: Payload):
    yt = YouTube(payload.url)

    streams = []
    for stream in yt.streams:
        streams += [Stream(
            type=stream.type,
            format=stream.mime_type.split("/")[-1],
            quality=stream.resolution if stream.type=="video" else stream.abr,
            fps=stream.fps if stream.type=="video" else "",
            codec=stream.video_codec if stream.type == "video" else stream.audio_codec 
        )]

    return streams