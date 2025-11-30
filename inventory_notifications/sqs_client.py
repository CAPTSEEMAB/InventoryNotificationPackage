import os
import json
import uuid
import boto3
from typing import Dict, List, Optional, Any
from datetime import datetime
from botocore.exceptions import ClientError


class SQSClient:

    def __init__(self, region: Optional[str] = None):
        self.region = region or os.getenv('AWS_SQS_REGION', 'us-east-1')
        self.sqs_client = boto3.client(
            'sqs',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=self.region
        )
        self.account_id = self._get_account_id()
        self._queue_urls: Dict[str, str] = {}

    def _get_account_id(self) -> str:
        try:
            sts = boto3.client('sts')
            return sts.get_caller_identity()['Account']
        except Exception:
            return "unknown"

    def _get_queue_url(self, queue_name: str) -> Optional[str]:
        if queue_name in self._queue_urls:
            return self._queue_urls[queue_name]

        try:
            response = self.sqs_client.get_queue_url(QueueName=queue_name)
            self._queue_urls[queue_name] = response['QueueUrl']
            return response['QueueUrl']
        except ClientError as e:
            if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
                return None
            raise

    def create_queue(self, queue_name: str, dead_letter_queue_arn: Optional[str] = None,
                     visibility_timeout: int = 30, message_retention_period: int = 1209600) -> str:
        existing_url = self._get_queue_url(queue_name)
        if existing_url:
            return existing_url

        attributes = {
            'VisibilityTimeoutSeconds': str(visibility_timeout),
            'MessageRetentionPeriod': str(message_retention_period),
            'ReceiveMessageWaitTimeSeconds': '20'
        }

        if dead_letter_queue_arn:
            attributes['RedrivePolicy'] = json.dumps({
                'deadLetterTargetArn': dead_letter_queue_arn,
                'maxReceiveCount': 3
            })

        response = self.sqs_client.create_queue(
            QueueName=queue_name,
            Attributes=attributes
        )
        queue_url = response['QueueUrl']
        self._queue_urls[queue_name] = queue_url
        return queue_url

    def send_message(self, queue_name: str, message_body: str, delay_seconds: int = 0) -> bool:
        queue_url = self._get_queue_url(queue_name)
        if not queue_url:
            return False

        try:
            self.sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=message_body,
                DelaySeconds=delay_seconds
            )
            return True
        except Exception:
            return False

    def receive_messages(self, queue_name: str, max_messages: int = 1, wait_time: int = 20) -> List[Dict[str, Any]]:
        queue_url = self._get_queue_url(queue_name)
        if not queue_url:
            return []

        response = self.sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=min(max_messages, 10),
            WaitTimeSeconds=wait_time,
            MessageAttributeNames=['All'],
            AttributeNames=['All']
        )

        messages = response.get('Messages', [])
        return messages
