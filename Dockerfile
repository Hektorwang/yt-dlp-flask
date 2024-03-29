FROM python:slim

# ENV <key1>=<value1> <key2>=<value2>...

# ARG user1=someuser

COPY app.py /yt-dlp-flask/
COPY cli_to_api.py /yt-dlp-flask/
COPY config.json /yt-dlp-flask/
COPY static /yt-dlp-flask/static

ADD requments.txt /yt-dlp-flask/
RUN sed -i.bak "s@http://deb.debian.org/debian@https://mirrors.tuna.tsinghua.edu.cn/debian@g" /etc/apt/sources.list.d/debian.sources && \
    apt-get -y update && apt-get -y upgrade && apt-get --no-install-recommends -y install ffmpeg && apt-get clean && \
    export PYTHONDONTWRITEBYTECODE=1 && \
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && pip install --no-cache-dir -r /yt-dlp-flask/requments.txt

WORKDIR /yt-dlp-flask/

EXPOSE 8000

CMD ["/usr/local/bin/gunicorn","--workers=1","--bind=0.0.0.0:8000","--log-level=debug","app:app"]
