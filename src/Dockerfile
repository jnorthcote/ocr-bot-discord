FROM python:3.8-slim-buster

WORKDIR /usr/src/bot

RUN apt update && apt install -y git tesseract-ocr libtesseract-dev libleptonica-dev pkg-config build-essential

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN mkdir sql

RUN pip install -U git+https://github.com/Rapptz/discord-ext-menus

CMD [ "python", "-u", "main.py" ]
