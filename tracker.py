
from tqdm import tqdm
from ultralytics import YOLO

import argparse
import os
import sys
from pathlib import Path

import cv2
import torch

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

import torch
import torch.nn as nn
from torchvision.models import resnet18, vgg11

import numpy as np

from script.Dataset import generate_bins, DetectedObject
from library.Math import *
from library.Plotting import *
from script import Model, ClassAverages
from script.Model import ResNet, ResNet18, VGG11

# model factory to choose model
model_factory = {
    'resnet': resnet18(pretrained=True),
    'resnet18': resnet18(pretrained=True),
    'vgg11': vgg11(pretrained=True)
}
regressor_factory = {
    'resnet': ResNet,
    'resnet18': ResNet18,
    'vgg11': VGG11
}

class Bbox:
    def __init__(self, box_2d, class_):
        self.box_2d = box_2d
        self.detected_class = class_

def plot3d(
    img,
    proj_matrix,
    box_2d,
    dimensions,
    alpha,
    theta_ray,
    img_2d=None
    ):

    # the math! returns X, the corners used for constraint
    location, X = calc_location(dimensions, proj_matrix, box_2d, alpha, theta_ray)

    orient = alpha + theta_ray

    if img_2d is not None:
        plot_2d_box(img_2d, box_2d)

    plot_3d_box(img, proj_matrix, orient, dimensions, location) # 3d boxes

    return location

def parse_opt():
    parser = argparse.ArgumentParser()

    parser.add_argument('--model_select', type=str, default='resnet18', help='Regressor model list: resnet, vgg, eff')
    parser.add_argument('--reg_weights', type=str, default='weights/resnet18.pkl', help='Regressor model weights')
    parser.add_argument('--output_path', type=str, default=ROOT / 'runs/track', help='Save output pat')
    parser.add_argument('--video', type=str, default='testvid.mp4', help='Video file path')
    parser.add_argument('--calib_file', type=str, default=ROOT / 'eval/camera_cal/calib_cam_to_cam.txt', help='Calibration file or path')

    opt = parser.parse_args()
    #opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1  # expand
    return opt

def main(filevideo, calib_file, model_select, reg_weights, output_path):
    model = YOLO('yolov8l.pt')
    video = cv2.VideoCapture(filevideo)
    frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    #frames = 50
    print(f"NUMBER OF FRAMES: {frames}")
    calib = str(calib_file)

    # load model
    base_model = model_factory[model_select]
    regressor = regressor_factory[model_select](model=base_model).cuda()

    # load weight
    checkpoint = torch.load(reg_weights)
    regressor.load_state_dict(checkpoint['model_state_dict'])
    regressor.eval()

    averages = ClassAverages.ClassAverages()
    angle_bins = generate_bins(2)


    output_video_frames = []
    # Process each frame
    for i in tqdm(range(frames), desc='Processing frames'):
        print(f'index {i}')
        ret, frame = video.read()

        if not ret:
            continue

        results = model.track(frame, persist=True, tracker='bytetrack.yaml', classes=0, verbose=False) 
        # Get result values
        boxes = results[0].boxes
        track_ids = []
        names = results[0].names

        if not boxes.is_track:
            continue

        try:
            track_ids = results[0].boxes.id.int().cpu().tolist()
        except Exception as e:
            track_ids = []

        for det, track_id in zip(results[0].boxes, track_ids):
            print(det)

            # bbox
            xyxy_ = [int(x) for x in det.xyxy[0]]
            top_left, bottom_right = (xyxy_[0], xyxy_[1]), (xyxy_[2], xyxy_[3])
            bbox = [top_left, bottom_right]
            label = "pedestrian"
            # print("bbox2d", bbox, label)

            cv2.putText(frame, f"{label} {track_id}", top_left, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)            
            

            try: 
                detectedObject = DetectedObject(frame, label, bbox, calib)
            except Exception as e:
                print("Could not create the DetectedObject")
                print(e)
                continue
            
            theta_ray = detectedObject.theta_ray
            input_img = detectedObject.img
            proj_matrix = detectedObject.proj_matrix
            detected_class = label

            input_tensor = torch.zeros([1,3,224,224]).cuda()
            input_tensor[0,:,:,:] = input_img

            # predict orient, conf, and dim
            [orient, conf, dim] = regressor(input_tensor)
            orient = orient.cpu().data.numpy()[0, :, :]
            conf = conf.cpu().data.numpy()[0, :]
            dim = dim.cpu().data.numpy()[0, :]

            dim += averages.get_item(detected_class)

            argmax = np.argmax(conf)
            orient = orient[argmax, :]
            cos = orient[0]
            sin = orient[1]
            alpha = np.arctan2(sin, cos)
            alpha += angle_bins[argmax]
            alpha -= np.pi

            # plot 3d detection
            plot3d(frame, proj_matrix, bbox, dim, alpha, theta_ray)

            #cv2.imshow("Person Tracking", frame)
            # Break the loop if 'q' is pressed
            #if cv2.waitKey(1) & 0xFF == ord("q"):
            #    break

        print("Done for img {i}")
        #print("saving to", f'{output_path}/testIMG_{i}.png')
        #cv2.imwrite(f'{output_path}/testIMG2_{i}.png', frame)
        output_video_frames.append(frame)

    # Save the output video
    out = cv2.VideoWriter(f'{output_path}/output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 15, (frame.shape[1], frame.shape[0]))
    for frame in output_video_frames:
        out.write(frame)
    out.release()



if __name__ == '__main__':
    args = parse_opt()
    filevideo = args.video
    # output_path = "runs/track"
    output_path = args.output_path
    # reg_weights = "weights/resnet18.pkl"
    reg_weights = args.reg_weights
    # model_select = "resnet18"
    model_select = args.model_select
    #filevideo, calib_file, model_select, output_path
    main(filevideo, args.calib_file, model_select, reg_weights, output_path)