# Fork para el CFC de YOLO3D

Del `README.md` sigue las instrucciones para crear un ambiente virtual con los requisitos necesarios y descarga los pesos del modelo resnet18.


```
python inference.py --weights yolov5s.pt --source  eval/parque_1080/ --reg_weights weights/resnet18.pkl --model_select resnet18 --output_path runs/parque_1080/ --save_result --calib_file eval/marcela_calib/testing.txt
```

# Tracker service

Para correr de forma local:

```
docker compose up
```

Se van a levantar los servicios de tracker y de locakstack (para poder simular guardar en un bucket de S3).

Es necesario subir el video y los pesos a traves del servicio tracker

```
curl -X POST  http://0.0.0.0:80/videos/upload -L -F "file=@tracker/testvid.mp4"
curl -X POST  http://0.0.0.0:80/weights/upload -L -F "file=@weights/resnet18.pkl"
```

Despues de ejecuta el tracker de la siguiente forma

```
curl -X POST "http://0.0.0.0:80/tracker" -H "Content-Type: application/json" -d '{
    "filename": "testvid.mp4",
    "weights" : "resnet18.pkl",
    "model_name": "yolo3d",
    "calib_matrix": "822.0 0.0 320.0 672.0 0.0 822.0 180.0 378.0 0.0 0.0 1.0 2.1"
}' -o output_video.mp4

```


Rebuild 

```
docker compose up -d --no-deps --build <service_name>
```

# Backup notes

**Necesito limpiar las siguientes notas, varias cosas no estan actualizadas**

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
docker compose up -d --no-deps --build tracker

# CURL

curl -X GET "http://0.0.0.0:80/videos/list"
curl -X POST  http://0.0.0.0:80/videos/upload -L -F "file=@tracker/testvid.mp4"
curl -X DELETE "http://0.0.0.0:80/videos/delete?filename=testvid.mp4"

curl -X GET "http://0.0.0.0:80/weights/list"
curl -X POST  http://0.0.0.0:80/weights/upload -L -F "file=@weights/resnet18.pkl"
curl -X DELETE "http://0.0.0.0:80/weights/delete?filename=resnet18.pkl"

curl -X POST "http://0.0.0.0:80/tracker" -H "Content-Type: application/json" -d '{
    "filename": "testvid.mp4",
    "weights" : "resnet18.pkl",
    "model_name": "yolo3d",
    "calib_matrix": "822.0 0.0 320.0 672.0 0.0 822.0 180.0 378.0 0.0 0.0 1.0 2.1"
}'


# Flow
curl -X POST  http://0.0.0.0:80/videos/upload -L -F "file=@tracker/testvid.mp4"
curl -X POST  http://0.0.0.0:80/weights/upload -L -F "file=@weights/resnet18.pkl"
curl -X GET "http://0.0.0.0:80/videos/list"
curl -X POST "http://0.0.0.0:80/tracker" -H "Content-Type: application/json" -d '{
    "filename": "testvid.mp4",
    "weights" : "resnet18.pkl",
    "model_name": "yolo3d",
    "calib_matrix": "822.0 0.0 320.0 672.0 0.0 822.0 180.0 378.0 0.0 0.0 1.0 2.1"
}' -o output_video.mp4

```

## Debug containers

```
# Curl localstack s3 bucket
aws configure # test, test, us-east-1, json
aws --endpoint-url=http://localhost:4566 s3 ls s3://my-test-bucket
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
