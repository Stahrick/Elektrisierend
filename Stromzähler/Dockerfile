FROM python:3.10
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY ./ ./
RUN chmod +x /app/app.py
CMD [ "python", "app.py"]