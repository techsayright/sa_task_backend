import json
import urllib.parse
import boto3
from PIL import Image
from io import BytesIO

print('Loading function')

s3 = boto3.client('s3')


def lambda_handler(event, context):

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    response = s3.get_object(Bucket=bucket, Key=key)

    image_content = response['Body'].read()

     # Resize the image
    image = Image.open(BytesIO(image_content))
    resized_image = image.resize((100, 100))  
    
    # Convert the resized image to bytes
    resized_image_bytes = BytesIO()
    resized_image.save(resized_image_bytes, format='png')
    resized_image_bytes.seek(0)
    
    # Upload the resized image to the destination bucket
    s3.put_object(Body=resized_image_bytes, Bucket="sa-task-imges-thumbnails", Key='d_100x100.png', ContentType='image/png', ACL = 'public-read')


    # print(response)
    return {"detail":"success"}
        
        