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

## Docker

```

docker build -t yolo3d_tracker -f cfc.Dockerfile

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
