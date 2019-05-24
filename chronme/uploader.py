import datetime
import platform

from .config_parser import ConfigParser
from .aws.s3 import S3Client

def upload_data(config: ConfigParser, events: dict, date: datetime):
    print("Uploading data")
    hostname = platform.node()
    for key_name in events.keys():
        if not key_name.endswith(hostname):
            new_key_name = key_name + "_" + hostname
            events[new_key_name] = events.pop(key_name)

    s3_client = S3Client(config.get_aws_config())
    s3_client.update_aw_day(date, events)
