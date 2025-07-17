import pytest
from moto import mock_aws
import boto3
from PIL import Image
import os
import io
import json

from .handler import handler


TEST_BUCKET = "test-bucket"
TEST_VIDEO_KEY = "test-video.mp4"


@pytest.fixture
def s3_setup(tmp_path):
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket=TEST_BUCKET)
        video_path = tmp_path / "test-video.mp4"
        os.system(f"ffmpeg -f lavfi -i color=c=red:s=320x240:d=2 -vf format=yuv420p {video_path}")
        with open(video_path, "rb") as f:
            s3.put_object(Bucket=TEST_BUCKET, Key=TEST_VIDEO_KEY, Body=f)
        yield s3


def test_video_thumbnail(s3_setup):
    event = {
        "bucket": TEST_BUCKET,
        "key": TEST_VIDEO_KEY,
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


def test_invalid_video_key(s3_setup):
    event = {
        "bucket": TEST_BUCKET,
        "key": "notfound.jpg",
        "output_key": "thumb/notfound.jpg",
        "size": [120, 120]
    }
    resp = handler(event)
    out = json.loads(resp)
    assert out["status"] == "error"
