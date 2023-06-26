from fastapi import FastAPI, UploadFile, File, Depends
from sqlalchemy.orm import Session
import boto3
import time
from .database import engine, get_db
from . import model
from .verify_token import verify_google_token
from .schema import ThumbCreate, GetThumbs, ThumbDetail

model.Base.metadata.create_all(bind=engine)

app = FastAPI()

supported_format = ['jpg', 'png', 'jpeg']

@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db), data: str = Depends(verify_google_token)):

    if not data:
        return {"detail": "Not Authenticated"}
    else:
        print(data)

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

@app.post("/stored_thumbnails")
def stored_thumbnails(new_thumb : ThumbCreate, db : Session = Depends(get_db)):
    get_id = db.query(model.original_img).filter(model.original_img.stored_filename == new_thumb.original_img_name).first()
    # print(get_id.id)

    s3_path = f'https://sa-task-imges-thumbnails.s3.amazonaws.com/{new_thumb.key}'

    new_data = model.thumbnail_img(**{"original_img_id": get_id.id, "filename": new_thumb.key, "s3_path" : s3_path, "thumb_size":new_thumb.thumb_size })

    db.add(new_data)
    db.commit()

    return {"detail":"success"}


@app.get("/list_original_imgs")
def list_original_imgs(db : Session = Depends(get_db)):
    list_detail = db.query(model.original_img).all()
    return list_detail


@app.post("/get_thumbnails")
def get_thumbnails(GetThumb: GetThumbs,db : Session = Depends(get_db)):
    data = db.query(model.thumbnail_img).filter(model.thumbnail_img.original_img_id == GetThumb.original_img_id).distinct(model.thumbnail_img.filename).all()
    return data 

@app.post("/thumb_details")
def thumb_details(ThumbDetails: ThumbDetail, db : Session = Depends(get_db)):
    data = db.query(model.thumbnail_img).filter(model.thumbnail_img.id == ThumbDetails.thumb_id).first()
    return data


