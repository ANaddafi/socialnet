import os
import json
import boto3
import subprocess
from urllib.parse import quote

# TODO: S3 credentials taken from env vars
s3 = boto3.client(
    's3',
    aws_access_key_id="test",
    aws_secret_access_key="test",
    aws_session_token="us-east-1",
)
def presigned_url(bucket, key, expires=600):
    return s3.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': key}, ExpiresIn=expires)


def download_thumb_with_ffmpeg(input_url, size=(200, 200)):
    output_path = "/tmp/thumb.jpg"
    command = [
        "ffmpeg",
        "-ss", "00:00:01",
        "-i", input_url,
        "-frames:v", "1",
        "-vf", f"scale={size[0]}:{size[1]}:force_original_aspect_ratio=decrease",
        "-y",
        output_path
    ]
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return output_path


def upload_file_to_s3(bucket, key, file_path, acl):
    # Note that ffmpeg writes to file by default, so we have a file instead of BytesIO here
    with open(file_path, 'rb') as f:
        s3.put_object(Bucket=bucket, Key=key, Body=f, ContentType="image/jpeg", ACL=acl)


def handler(event, context=None):
    # event: { "bucket": "...", "key": "...", "output_key": "...", "size": [w, h] }
    try:
        data = event if isinstance(event, dict) else json.loads(event)
        bucket = data['bucket']
        key = data['key']
        output_key = data.get('output_key') or f"thumb/{os.path.splitext(os.path.basename(key))[0]}.jpg"
        size = tuple(data.get('size', [200, 200]))
        acl = data.get('acl', 'public-read')

        input_url = presigned_url(bucket, key, expires=300)
        output_path = download_thumb_with_ffmpeg(input_url, size)
        upload_file_to_s3(bucket, output_key, output_path, acl)

        return json.dumps({
            "status": "success",
            "output_key": output_key,
        })
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})
