from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session
import boto3
import time
from .database import engine, get_db
from . import model
from .verify_token import verify_google_token

model.Base.metadata.create_all(bind=engine)

app = FastAPI()

supported_format = ['jpg', 'png', 'jpeg']

@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db), data: str = Depends(verify_google_token)):

    print(data, '1')

    image_load = await file.read()

    if(supported_format.count(file.filename.split(".")[-1]) == 0):
        return {"detail" : "Not Supported file format"}

    key_file_name = round(time.time()*1000)

    client = boto3.client('s3', region_name='us-east-1')
    client.put_object(Body=image_load, Bucket='sa-task-imges', Key=f'{key_file_name}.{file.filename.split(".")[-1]}', ContentType= file.headers['content-type'], ACL = 'public-read')

    print(f'https://sa-task-imges.s3.amazonaws.com/{key_file_name}.{file.filename.split(".")[-1]}')

    new_data = model.original_img(**{"actual_filename":file.filename, "stored_filename":f'{key_file_name}.{file.filename.split(".")[-1]}', "file_size": file.size, "s3_path": f'https://sa-task-imges.s3.amazonaws.com/{key_file_name}.{file.filename.split(".")[-1]}', "file_format" : file.filename.split(".")[-1]})

    db.add(new_data)
    db.commit()

    return {"detail": "success"}






