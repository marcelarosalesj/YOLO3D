FROM ubuntu:22.04

WORKDIR /code

RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip

COPY ./requirements-cfc.txt /code/requirements-cfc.txt

#RUN pip install -r /code/requirements.txt

#RUN conda create --name yolo3d --file conda-requirements-cfc.txt
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install vim -y
RUN apt install python3.11 -y
RUN python3.11 -m pip install --upgrade pip
RUN pip3.11 install -r /code/requirements-cfc.txt

COPY ./library /code/library
COPY ./script /code/script
COPY ./weights /code/weights
COPY ./tracker /code/tracker

RUN export PYTHONPATH=$PYTHONPATH:/code:/code

EXPOSE 80

CMD ["fastapi", "run", "tracker/app.py", "--port", "80"]
