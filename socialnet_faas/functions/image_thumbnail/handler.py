import os
import json
import boto3
from PIL import Image
from io import BytesIO

# TODO: S3 credentials taken from env vars
s3 = boto3.client(
    's3',
    aws_access_key_id="test",
    aws_secret_access_key="test",
    aws_session_token="us-east-1",
)


def download_image_from_s3(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    return BytesIO(response['Body'].read())


def upload_image_to_s3(bucket, key, image_bytes, acl):
    s3.put_object(Bucket=bucket, Key=key, Body=image_bytes, ContentType='image/jpeg', ACL=acl)


def handler(event, context=None):
    # event: { "bucket": "...", "key": "...", "output_key": "...", "size": [w, h] }
    try:
        data = event if isinstance(event, dict) else json.loads(event)
        bucket = data['bucket']
        key = data['key']
        output_key = data.get('output_key') or f"thumb/{os.path.basename(key)}"
        size = tuple(data.get('size', [200, 200]))
        acl = data.get('acl', 'public-read')

        image_bytes = download_image_from_s3(bucket, key)
        with Image.open(image_bytes) as img:
            img.thumbnail(size)
            output_buffer = BytesIO()
            img.save(output_buffer, format='JPEG')
            output_buffer.seek(0)
            upload_image_to_s3(bucket, output_key, output_buffer.getvalue(), acl)

        return json.dumps({
            "status": "success",
            "output_key": output_key,
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
