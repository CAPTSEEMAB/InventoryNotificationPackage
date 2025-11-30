import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from .sqs_client import SQSClient
from .interfaces import QueueMessage, NotificationPayload


class NotificationQueueService:
    """Lightweight notification queue service integrating SQS + SNS.

    The service attempts to queue notifications to SQS and falls back to SNS
    direct publish if queuing is disabled or fails.
    """

    def __init__(self, sqs_client: Optional[SQSClient] = None):
        self.sqs_client = sqs_client or SQSClient()
        self.enabled = os.getenv('SQS_ENABLE_NOTIFICATIONS', 'true').lower() == 'true'
        self.notification_queue = os.getenv('AWS_SQS_QUEUE_NAME', 'notification-processing-queue')
        self.dlq_queue = os.getenv('AWS_SQS_DLQ_NAME', 'notification-dead-letter-queue')

    def queue_notification(self, notification: NotificationPayload, delay_seconds: int = 0, priority: str = "normal") -> bool:
        if not self.enabled:
            return self._send_direct_notification(notification)

        message = QueueMessage(
            id=str(uuid.uuid4()),
            message_type="email_notification",
            payload={"notification": notification.model_dump(), "priority": priority, "queued_at": datetime.now().isoformat()},
            retry_count=0,
            max_retries=3,
            created_at=datetime.now()
        )

        return self.sqs_client.send_message(self.notification_queue, message.model_dump_json(), delay_seconds)

    def _send_direct_notification(self, notification: NotificationPayload) -> bool:
        try:
            import boto3
            sns_client = boto3.client('sns', region_name=os.getenv('AWS_REGION', 'us-east-1'))
            topic_arn = os.getenv('AWS_SNS_TOPIC_ARN')
            if not topic_arn:
                return False
            response = sns_client.publish(TopicArn=topic_arn, Subject=notification.subject, Message=notification.message)
            return response.get('MessageId') is not None
        except Exception:
            return False
