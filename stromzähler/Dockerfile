FROM python:3.10
RUN useradd -ms /bin/bash uwsgi
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY ./ ./
RUN chown -R uwsgi /app
RUN chmod +x /app/app.py
CMD ["uwsgi", "--socket", "0.0.0.0:25565", "--protocol=http", "--uid=uwsgi", "--enable-threads", "-w", "wsgi:app"]