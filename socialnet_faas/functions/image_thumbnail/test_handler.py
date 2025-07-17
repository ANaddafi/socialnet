import pytest
from moto import mock_aws
from PIL import Image
import boto3
import io
import json

from .handler import handler

TEST_BUCKET = "test-bucket"
TEST_IMAGE_KEY = "test-image.jpg"


@pytest.fixture
def s3_setup():
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=TEST_BUCKET)
        # Create a simple test image and upload to S3
        img = Image.new('RGB', (800, 600), color='blue')
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        buf.seek(0)
        s3.put_object(Bucket=TEST_BUCKET, Key=TEST_IMAGE_KEY, Body=buf.getvalue())
        yield s3


def test_image_thumbnail(s3_setup):
    event = {
        "bucket": TEST_BUCKET,
        "key": TEST_IMAGE_KEY,
        "output_key": "thumb/test-thumb.jpg",
        "size": [120, 120]
    }
    resp = handler(event)
    out = json.loads(resp)
    assert out["status"] == "success"

    result_key = out["output_key"]
    s3 = s3_setup
    obj = s3.get_object(Bucket=TEST_BUCKET, Key=result_key)
    img = Image.open(io.BytesIO(obj['Body'].read()))
    assert img.size[0] <= 120 and img.size[1] <= 120


def test_invalid_image_key(s3_setup):
    event = {
        "bucket": TEST_BUCKET,
        "key": "notfound.jpg",
        "output_key": "thumb/notfound.jpg",
        "size": [120, 120]
    }
    resp = handler(event)
    out = json.loads(resp)
    assert out["status"] == "error"
