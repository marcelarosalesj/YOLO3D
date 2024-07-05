from fastapi import FastAPI, File, UploadFile
from fastapi import FastAPI, status
import boto3

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


app = FastAPI()

# TODO: use two different buckets for videos and for weights


@app.get("/")
def read_root():
    return {"Hello": "Uploader!"}

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

