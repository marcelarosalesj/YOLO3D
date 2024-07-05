FROM ubuntu:22.04

WORKDIR /code

RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install vim -y
RUN apt install python3.11 -y
RUN python3.11 -m pip install --upgrade pip

RUN pip3.11 install boto3
RUN pip3.11 install botocore
RUN pip3.11 install fastapi

COPY ./uploader /code/uploader

RUN export PYTHONPATH=$PYTHONPATH:/code:/code

EXPOSE 80

CMD ["fastapi", "run", "uploader/app.py", "--port", "81"]
