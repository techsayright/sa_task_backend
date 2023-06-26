import json
import urllib.parse
import boto3
from PIL import Image
from io import BytesIO
import requests

print('Loading function')

s3 = boto3.client('s3')


def lambda_handler(event, context):

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    image_name = event['Records'][0]['s3']['object']['key']
    image_name_wout_ext = event['Records'][0]['s3']['object']['key'].split(".")[0]
    
    response = s3.get_object(Bucket=bucket, Key=key)

    image_content = response['Body'].read()

     # Resize the image
    image = Image.open(BytesIO(image_content))

    resize_dimensions = [
        (100, 100),
        (200, 150),
        (150, 200)
    ]
    
    for i, dimensions in enumerate(resize_dimensions):
        resized_image = image.resize(dimensions)
        resized_image_bytes = BytesIO()
        resized_image.save(resized_image_bytes, format='png')
        resized_image_bytes.seek(0)
        resized_image_key = f'{image_name_wout_ext}_{dimensions[0]}x{dimensions[1]}.png'
        s3.put_object(
            Body=resized_image_bytes,
            Bucket="sa-task-imges-thumbnails",
            Key=resized_image_key,
            ContentType='image/png',
            ACL='public-read'
        )
    
        req_data = json.dumps({
            "original_img_name": image_name,
            "key": resized_image_key,
            "thumb_size": len(resized_image_bytes.getvalue())
        })
        api_res = requests.post("http://0.tcp.in.ngrok.io:13729/stored_thumbnails", headers={"Content-Type": "application/json"}, data=req_data)

        if api_res.status_code != 200:
            print("Error storing image:", resized_image_key)
            return {"detail": "fail"}
        
    return {"detail":"success"}

   