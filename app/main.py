from fastapi import FastAPI, UploadFile, File, Depends, status, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import boto3
import time
from .database import engine, get_db
from . import model
from .verify_token import verify_google_token
from .schema import ThumbCreate

model.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = boto3.client('s3', region_name='us-east-1')

supported_format = ['jpg', 'png', 'jpeg']

@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db), data: str = Depends(verify_google_token)):
# async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):

    # if not data:
    #     return {"detail": "Not Authenticated"}
    # else:
    #     print(data)

    image_load = await file.read()

    if(supported_format.count(file.filename.split(".")[-1]) == 0):
        return {"detail" : "Not Supported file format"}

    key_file_name = round(time.time()*1000)

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
def list_original_imgs(db : Session = Depends(get_db),data: str = Depends(verify_google_token)):
    list_detail = db.query(model.original_img).all()
    return list_detail

@app.get("/list_original_imgs/{id}")
def list_original_img(id: int, db : Session = Depends(get_db), data: str = Depends(verify_google_token)):
    data = db.query(model.original_img).filter(model.original_img.id == id).first()
    return data

@app.get("/get_thumbnails/{id}")
def get_thumbnails(id: int,db : Session = Depends(get_db), data: str = Depends(verify_google_token)):
    data = db.query(model.thumbnail_img).filter(model.thumbnail_img.original_img_id == id).distinct(model.thumbnail_img.filename).all()
    return data 

@app.get("/thumb_details/{id}")
def thumb_details(id: int, db : Session = Depends(get_db), data: str = Depends(verify_google_token)):
    data = db.query(model.thumbnail_img).filter(model.thumbnail_img.id == id).first()
    return data

@app.get("/delete_image/{id}")
def delete_image(id: int, db : Session = Depends(get_db),data: str = Depends(verify_google_token)):
    img_data = db.query(model.original_img).filter(model.original_img.id == id)

    if not img_data.first():
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail=f"requested id {id} for delete image was not found!")
    
    img_key = img_data.first().stored_filename

    client.delete_object(Bucket='sa-task-imges', Key=img_key)

    thumb_data = db.query(model.thumbnail_img).filter(model.thumbnail_img.original_img_id == id)

    if not thumb_data.first():
        img_data.delete(synchronize_session=False)
        db.commit()
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="its thumbnails not found!")
    
    thumb_key= thumb_data.all()

    for i,v in enumerate(thumb_key):
        client.delete_object(Bucket='sa-task-imges-thumbnails', Key=v.__dict__['filename'])

    img_data.delete(synchronize_session=False)
    db.commit()

    return {"detail":"success"}



