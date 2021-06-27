import youtube_dl

ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '96',
        }]
    }

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    result = ydl.extract_info("https://open.spotify.com/album/4Sj1MJMO2jaIZyr00ipCkl")
    print('done')