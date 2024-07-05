#!/bin/bash


curl -X POST http://0.0.0.0:81/videos/upload -L -F "file=@tracker/testvid.mp4"
curl -X POST http://0.0.0.0:81/weights/upload -L -F "file=@weights/resnet18.pkl"
curl -X GET  http://0.0.0.0:81/weights/list




curl -X POST "http://0.0.0.0:80/tracker" -H "Content-Type: application/json" -d '{
    "filename": "testvid.mp4",
    "weights" : "resnet18.pkl",
    "model_name": "yolo3d",
    "calib_matrix": "822.0 0.0 320.0 672.0 0.0 822.0 180.0 378.0 0.0 0.0 1.0 2.1"
}' -o output_video.mp4
