FROM python:3.11

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY ./src /app/src
COPY location.json /app/location.json


VOLUME [ "/data" ]

CMD ["python", "src/main.py"]