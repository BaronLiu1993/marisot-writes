import boto3
from dotenv import load_dotenv
import os
import logging
from botocore.exceptions import ClientError
import requests
from io import BytesIO
import fitz

from pymongo import MongoClient
from service.tools.constants import MONGODB_URI

load_dotenv()
logging.basicConfig(level=logging.INFO)

# AWS S3 Configuration
bucket_name = os.getenv("AWS_S3_BUCKET_NAME")
object_name = os.getenv("AWS_S3_OBJECT_NAME")

# Initialize MongoDB client and collection
mongo_client = MongoClient(uri=MONGODB_URI)
database = mongo_client["database"]
metadata_collection = database.get_collection("metadata")
memory_collection = database.get_collection("memory")

# Initialize S3 client
s3_client = boto3.client('s3')

def upload_to_s3():
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_name},
            ExpiresIn=3600,
        )
    except ClientError as e:
        logging.error(e)
        return None

    logging.info(f"Generated presigned URL: {response}")
    return response

def save_file_metadata_to_mongo(file_metadata):
    try:
        result = memory_collection.insert_one(file_metadata)
        logging.info(f"File metadata saved to MongoDB with ID: {result.inserted_id}")
    except Exception as e:
        logging.error(f"Error saving file metadata to MongoDB: {e}")

def parse_file_(s3_url):
    response = requests.get(s3_url)
    response.raise_for_status() 

    pdf_stream = BytesIO(response.content)
    doc = fitz.open(stream=pdf_stream, filetype='pdf')

    logging.info(f"Finished Parsing PDF")
    doc.close()