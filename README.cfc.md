# Fork para el CFC de YOLO3D

Del `README.md` sigue las instrucciones para crear un ambiente virtual con los requisitos necesarios y descarga los pesos del modelo resnet18.

```
python inference.py --weights yolov5s.pt --source  eval/parque_1080/ --reg_weights weights/resnet18.pkl --model_select resnet18 --output_path runs/parque_1080/ --save_result --calib_file eval/marcela_calib/testing.txt
```