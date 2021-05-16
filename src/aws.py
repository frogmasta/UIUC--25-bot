import os

import boto3
from dotenv import load_dotenv

load_dotenv()
ACCESS_KEY = os.getenv('AMAZON_ACCESS_KEY')
SECRET_KEY = os.getenv('AMAZON_SECRET_KEY')
BUCKET = os.getenv('AMAZON_BUCKET')


def upload_to_aws(fp, s3_file_name):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        s3.upload_file(fp, BUCKET, s3_file_name)
        return True
    except Exception as e:
        print(e)
        return False
