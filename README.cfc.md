# Fork para el CFC de YOLO3D

Del `README.md` sigue las instrucciones para crear un ambiente virtual con los requisitos necesarios y descarga los pesos del modelo resnet18.


```
python inference.py --weights yolov5s.pt --source  eval/parque_1080/ --reg_weights weights/resnet18.pkl --model_select resnet18 --output_path runs/parque_1080/ --save_result --calib_file eval/marcela_calib/testing.txt
```

## Tracker

```
# Va a correr el tracker sobre `testvid.mp4`
python tracker.py --output_path=runs/
```



Aqui encontre informacion adicional sobre motocicleta y autobus
https://github.com/patrickcho168/3dbb/blob/master/torch_lib/class_averages.txt


## Docker compose

```
docker compose up
docker compose down --rmi all

# rebuild image
docker compose up -d --no-deps --build yolo3d_tracker 

# CURL

curl -X GET "http://0.0.0.0/listFiles"
curl -X POST  http://0.0.0.0:80/uploadFile -L -F "file=@tracker/testvid.mp4"
curl -X DELETE "http://0.0.0.0/deleteFile?filename=testvid.mp4"


curl -X GET "http://0.0.0.0/videos/list"
curl -X POST  http://0.0.0.0:80/videos/upload -L -F "file=@tracker/testvid.mp4"
curl -X DELETE "http://0.0.0.0/videos/delete?filename=testvid.mp4"



aws configure # test, test, us-east-1, json
aws --endpoint-url=http://localhost:4566 s3 ls s3://my-test-bucket


curl -X POST "http://0.0.0.0/run_tracker?filename=testvid.mp4"

```

## Docker

```

docker build -t yolo3d_tracker -f cfc.Dockerfile .

docker run -it --rm -p 80:80 --name tracker --gpus all  yolo3d_tracker

docker image rm yolo3d_tracker:latest


```


Inside the container
```
docker exec -it tracker bash

export PYTHONPATH=/code; python3.11 tracker/main.py
```

## API

```
curl http://localhost:80/
```
