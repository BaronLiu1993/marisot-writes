import re
from datetime import datetime, timezone
from pathlib import Path

import boto3
from pymongo import MongoClient

from dto.plan_dto import MemorySchema
from service.tools.constants import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_S3_ENDPOINT,
    AWS_SECRET_ACCESS_KEY,
    MONGODB_URI,
)

mongo_client = MongoClient(MONGODB_URI)
database = mongo_client["database"]
memory_collection = database.get_collection("memory")
metadata_collection = database.get_collection("metadata")
file_collection = database.get_collection("file_documents")

def build_s3_client():
    kwargs = {"region_name": AWS_REGION}
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        kwargs["aws_access_key_id"] = AWS_ACCESS_KEY_ID
        kwargs["aws_secret_access_key"] = AWS_SECRET_ACCESS_KEY
    if AWS_S3_ENDPOINT:
        kwargs["endpoint_url"] = AWS_S3_ENDPOINT
    return boto3.client("s3", **kwargs)


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.rstrip() for line in text.splitlines())
    return text.strip()

def insert_file_metadata(user_id, thread_id, filename, file_url):
    metadata_collection.insert_one({
        "user_id": user_id,
        "thread_id": thread_id,
        "filename": filename,
        "mimeType": Path(filename).suffix,
        "file_url": file_url,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

def upload_file_to_s3(user_id, thread_id, bucket, object_key, expires_in=3600, content_type="application/octet-stream"):
    s3_client = build_s3_client()
    presigned_url = s3_client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": bucket,
            "Key": object_key,
            "ContentType": content_type,
        },
        ExpiresIn=expires_in,
    )

    file_url = f"s3://{bucket}/{object_key}"
    insert_file_metadata(user_id, thread_id, object_key, file_url)
    return {
        "upload_url": presigned_url,
        "file_url": file_url,
        "bucket": bucket,
        "object_key": object_key,
        "expires_in": expires_in,
    }

