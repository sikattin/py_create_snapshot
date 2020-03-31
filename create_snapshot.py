#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
import os
import boto3
import logging
from datetime import datetime
from botocore.exceptions import BotoCoreError, ClientError


logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    # volume tag
    tag = os.environ['TAG']
    args = {
        "Filters": [
            {
                "Name": "tag:{0}".format(tag),
                "Values": [
                    "True"
                ]
            }
        ]
    }
    try:
        client = boto3.client('ec2')
        # Get volume list with tagged Snapshot is True
        response = client.describe_volumes(**args)
        # Create Snapshots
        for volume in response['Volumes']:
            volumeid = volume['VolumeId']
            res = client.create_snapshot(
                Description='Created by lambda',
                VolumeId=volumeid,
                TagSpecifications=[
                    {
                        'ResourceType': 'snapshot',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': 'Snapshot-{0}-{1}'.format(
                                    volumeid,
                                    datetime.now().strftime("%Y%m%d")
                                )
                            }
                        ]
                    }
                ]
            )
    except (ClientError, BotoCoreError) as e:
        logger.error('Raised unexpected exception')
        logger.exception(str(e))
    else:
        if res['State'] != 'error':
            logger.info('Succeeded creating a snapshot of {0}'.format(volumeid))
        else:
            logger.error('Error has occured during creating a snapshot of {0}' \
                .format(volumeid)
            )
