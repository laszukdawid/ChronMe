import datetime
import logging
import platform

from .config_parser import ConfigParser
from .aws.s3 import S3Client

logger = logging.getLogger(__name__)

def upload_data(config: ConfigParser, events: dict, date: datetime.date):
    """Uploads data to s3.
    :config ConfigParser: Contains info about local rules, s3 path and such like.
    :events dict: Holds all events in ActivityWatch specific buckets.
    :date datetime.date: Date for which events are uploaded.
    """
    logger.info("Uploading data")
    hostname = platform.node()
    logger.debug(hostname)

    # Logic here tries to append your hostname to AW buckets.
    # This is needed in case we want to sync data with other machines could've been
    # used the same day with the same watchers.
    for key_name in events.keys():
        if key_name.endswith(hostname):
            continue
        new_key_name = key_name + "_" + hostname
        events[new_key_name] = events.pop(key_name)

    s3_client = S3Client(config.get_aws_config())
    responses = s3_client.update_aw_day(date, events)
    logger.info("Uploaded %i files", len(responses))
