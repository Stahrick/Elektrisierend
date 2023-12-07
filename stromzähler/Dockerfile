FROM python:3.10
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY ./ ./
RUN chmod +x /app/app.py
CMD ["uwsgi", "--socket", "0.0.0.0:25565", "--protocol=http", "-w", "wsgi:app"]