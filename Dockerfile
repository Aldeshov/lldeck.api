FROM python:3.9.13

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install -r ./requirements.txt

COPY . /app
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./entrypoint.sh .

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
