import json

from datetime import date, datetime, timedelta
import boto3
from botocore.errorfactory import ClientError

class AwsClient:

    CONFIG_PROFILE_NAME = "profile"
    CONFIG_S3_BUCKET = "s3Bucket"
    CONFIG_S3_PATH = "s3Path"

    def __init__(self, config: dict): 
        self.config = config

        self._session = boto3.session.Session(profile_name=config[self.CONFIG_PROFILE_NAME])
        self._s3 = self._session.client('s3')

        self._check_or_create_bucket()
    
    def _check_or_create_bucket(self):
        s3_bucket = self.config[self.CONFIG_S3_BUCKET]
        s3_path = self.config[self.CONFIG_S3_PATH]
        try:
            self._s3.head_object(Bucket=s3_bucket, Key=s3_path)
        except ClientError:
            self._s3.create_bucket(Bucket=s3_bucket)

    def update_aw_day(self, date, all_buckets_events: dict):
        date_key = date.isoformat()[:10]
        for aw_bucket_name, aw_bucket_events in all_buckets_events.items():
            s3_path = '/'.join([self.config[self.CONFIG_S3_PATH], date_key, aw_bucket_name + '.json'])
            self._upload_json(self.config[self.CONFIG_S3_BUCKET], s3_path, aw_bucket_events)
    
    def _upload_json(self, bucket: str, key: str, json_data: dict):
        self._s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=(bytes(json.dumps(json_data, default=self._json_serializer).encode('UTF-8')))
        )

    @staticmethod
    def _json_serializer(obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, timedelta):
            return obj.total_seconds()
        raise TypeError ("Type %s not serializable" % type(obj))