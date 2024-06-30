import os
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, File, UploadFile
from fastapi import FastAPI, status

import boto3
import uvicorn
from botocore.exceptions import NoCredentialsError

from .tracker import yolo3d_tracker

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

@app.get("/")
def read_root():
    return {"Hello": "Tracker!"}

@app.post("/uploadFile", status_code=status.HTTP_200_OK)
async def upload_file(file: UploadFile = File(...)):
    print(f"file = {file}")
    print(f"file type={type(file)}")
    # Save file in a bucket
    try:
        s3_client.upload_fileobj(file.file, AWS_BUCKET_NAME, file.filename)
        return {"filename": file.filename}
    except NoCredentialsError:
        return {"error": "Invalid credentials"}

@app.delete("/deleteFile", status_code=status.HTTP_200_OK)
async def delete_file(filename: str):
    print(f"deleting file {filename}...")
    try:
        s3_client.delete_object(Bucket=AWS_BUCKET_NAME, Key=filename)
        return {"status": "success", "filename": filename}
    except NoCredentialsError:
        return {"error": "Invalid credentials"}

@app.get("/listFiles", status_code=status.HTTP_200_OK)
async def list_files():
    try:
        response = s3_client.list_objects_v2(Bucket=AWS_BUCKET_NAME)
        files = [item['Key'] for item in response.get('Contents', [])]
        return {"files": files}
    except NoCredentialsError:
        return {"error": "Invalid credentials"}

@app.post("/tracker", status_code=status.HTTP_200_OK)
async def run_tracker(filename: str):
    try:
        print(f"file = {filename}")
        # Define local path for the downloaded file
        local_file_path = f"/tmp/{filename}"
        print(f"file local = {local_file_path}")
        # Create the /tmp directory if it doesn't exist
        os.makedirs("/tmp", exist_ok=True)
        
        # Download the file from the S3 bucket
        s3_client.download_file(AWS_BUCKET_NAME, filename, local_file_path)

        # Verify if the file was downloaded
        if os.path.exists(local_file_path):
            print(f"File {local_file_path} downloaded successfully.")
        else:
            print(f"File {local_file_path} was not downloaded.")
        
        # Run the YOLO3D tracker function
        print(f"after yolo3d")
        yolo3d_tracker(local_file_path)
        print(f"before yolo3d")
        import time
        time.sleep(5)
        # Clean up: remove the local file after processing
        os.remove(local_file_path)
        
        return {"status": "success", "filename": filename}
    except NoCredentialsError:
        return {"error": "Invalid credentials"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)