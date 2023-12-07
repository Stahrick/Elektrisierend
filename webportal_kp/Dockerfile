FROM python:3.10
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY ./ ./
RUN chmod +x /app/web_server.py
CMD [ "uwsgi", "--socket", "0.0.0.0:4000", "--protocol=http", "-w", "wsgi:app"]
