FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt

# COPY .env .env

COPY src src
WORKDIR /app/src

ENTRYPOINT [ "python3" ]
CMD [ "main.py" ]
