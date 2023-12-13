FROM python:3.8-slim-buster

# Set Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set Working directory
WORKDIR /zeron

COPY . .

RUN python3 -m pip install --upgrade pip

RUN apt update
RUN apt install git -y

# Install required packages
RUN python3 -m pip install -r /zeron/requirements.txt