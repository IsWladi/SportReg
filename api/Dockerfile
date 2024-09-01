FROM python:3.12.5-slim-bullseye
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN rm /code/requirements.txt
COPY ./app /code/app
