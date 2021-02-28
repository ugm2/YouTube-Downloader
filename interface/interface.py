import streamlit as st
import requests
import pandas as pd
import os
import base64

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href

@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def get_streams(url):
    params = {'url': url}
    response = requests.post(
        "http://localhost:5001/list_streams",
        json=params
    )
    
    result = response.json()
    
    return result

def download_video(data):
    response = requests.post(
        "http://localhost:5001/download",
        json=data
    )
    
    result = response.json()
    
    return result

def interface():
    st.header("Youtube Downloader")

    url = st.text_input("Introduce a YouTube URL")

    if url:
        with st.spinner("Sending request..."):
            streams = get_streams(url)
        
        if streams:
            df = pd.DataFrame(streams)

            video_types = list(set(df['type']))
            video_type = st.selectbox("Select type", video_types)

            df = df[df['type']==video_type]

            mime_types = list(set(df['mime_type']))
            mime_type = st.selectbox("Mime type", mime_types)

            df = df[df['mime_type']==mime_type]

            if video_type == "video":
                resolutions = sorted(list(set(df['res'])), reverse=True)
                resolution = st.selectbox("Resolution", resolutions)
                df = df[df['res']==resolution]

                fpss = sorted(list(set(df['fps'])), reverse=True)
                fps = st.selectbox("FPS", fpss)
                df = df[df['fps']==fps]

                video_codecs = list(set(df['video_codec']))
                video_codec = st.selectbox("Video Codec", video_codecs)
                df = df[df['video_codec']==video_codec]
            else:
                bitrates = list(set(df['bitrate']))
                bitrate = st.selectbox("Bitrate", bitrates)
                df = df[df['bitrate']==bitrate]

                audio_codecs = list(set(df['audio_codec']))
                audio_codec = st.selectbox("audio Codec", audio_codecs)
                df = df[df['audio_codec']==audio_codec]

            if st.button("Download"):
                df.dropna(axis=1, inplace=True)
                data = df.to_dict('records')[0]
                gif_runner = st.image("assets/loading.gif")
                file_path = download_video(data)

                if file_path:
                    st.markdown(
                        get_binary_file_downloader_html(
                            file_path, "file to your PC"),
                            unsafe_allow_html=True)
                    gif_runner.empty()



interface()