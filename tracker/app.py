import os
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, File, UploadFile
from fastapi import FastAPI, status
from pydantic import BaseModel

import boto3
import uvicorn
from botocore.exceptions import NoCredentialsError

from .tracker import video_tracker

app = FastAPI()

AWS_ACCESS_KEY_ID = 'test'
AWS_SECRET_ACCESS_KEY = 'test'
AWS_BUCKET_NAME = 'my-test-bucket'
AWS_REGION = 'us-east-1'

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
    endpoint_url='http://localstack:4566'
)

try:
    s3_client.create_bucket(Bucket=AWS_BUCKET_NAME)
except s3_client.exceptions.BucketAlreadyExists:
    pass
except s3_client.exceptions.BucketAlreadyOwnedByYou:
    pass

class TrackerParams(BaseModel):
    filename: str
    weights: str
    model_name: str
    calib_matrix: str

@app.get("/")
def read_root():
    return {"Hello": "Tracker!"}

@app.post("/videos/upload", status_code=status.HTTP_200_OK)
async def upload_video(file: UploadFile = File(...)):
    print(f"Uploading {file.filename}")
    try:
        s3_client.upload_fileobj(file.file, AWS_BUCKET_NAME, file.filename)
        return {"filename": file.filename}
    except NoCredentialsError:
        return {"error": "Invalid credentials"}

@app.delete("/videos/delete", status_code=status.HTTP_200_OK)
async def delete_video(filename: str):
    print(f"Deleting {filename}...")
    try:
        s3_client.delete_object(Bucket=AWS_BUCKET_NAME, Key=filename)
        return {"status": "success", "filename": filename}
    except NoCredentialsError:
        return {"error": "Invalid credentials"}

@app.get("/videos/list", status_code=status.HTTP_200_OK)
async def list_videos():
    print(f"Getting list of videos")
    try:
        response = s3_client.list_objects_v2(Bucket=AWS_BUCKET_NAME)
        files = [item['Key'] for item in response.get('Contents', [])]
        return {"files": files}
    except NoCredentialsError:
        return {"error": "Invalid credentials"}

# TODO: use two different buckets for videos and for weights

@app.post("/weights/upload", status_code=status.HTTP_200_OK)
async def upload_video(file: UploadFile = File(...)):
    print(f"Uploading {file.filename}")
    try:
        s3_client.upload_fileobj(file.file, AWS_BUCKET_NAME, file.filename)
        return {"filename": file.filename}
    except NoCredentialsError:
        return {"error": "Invalid credentials"}

@app.delete("/weights/delete", status_code=status.HTTP_200_OK)
async def delete_video(filename: str):
    print(f"Deleting {filename}...")
    try:
        s3_client.delete_object(Bucket=AWS_BUCKET_NAME, Key=filename)
        return {"status": "success", "filename": filename}
    except NoCredentialsError:
        return {"error": "Invalid credentials"}

@app.get("/weights/list", status_code=status.HTTP_200_OK)
async def list_weights():
    print(f"Getting list of weights")
    try:
        response = s3_client.list_objects_v2(Bucket=AWS_BUCKET_NAME)
        files = [item['Key'] for item in response.get('Contents', [])]
        return {"files": files}
    except NoCredentialsError:
        return {"error": "Invalid credentials"}


@app.post("/tracker", status_code=status.HTTP_200_OK)
async def tracker(params: TrackerParams):
    try:
        filename = params.filename
        weights = params.weights
        model_name = params.model_name
        calib_matrix = params.calib_matrix

        print(f"Getting {filename} from bucket")
        local_file_path = f"/tmp/{filename}"
        os.makedirs("/tmp", exist_ok=True)
        s3_client.download_file(AWS_BUCKET_NAME, filename, local_file_path)

        if os.path.exists(local_file_path):
            print(f"File {local_file_path} downloaded successfully.")
        else:
            print(f"File {local_file_path} was not downloaded.")

        print(f"Getting {weights} from bucket")
        weights_local_file_path = f"/tmp/{weights}"
        s3_client.download_file(AWS_BUCKET_NAME, weights, weights_local_file_path)

        if os.path.exists(weights_local_file_path):
            print(f"File {weights_local_file_path} downloaded successfully.")
        else:
            print(f"File {weights_local_file_path} was not downloaded.")

        if not model_name:
            model_name = "yolo3d"
        video_tracker(local_file_path,
                      weights_local_file_path,
                      model_name=model_name,
                      calib_matrix=calib_matrix)

        os.remove(local_file_path)

        return {"status": "success", "filename": filename}
    except NoCredentialsError:
        return {"error": "Invalid credentials"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
