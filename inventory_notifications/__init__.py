"""inventory_notifications (isolated packaging workspace)

Copied from the InventoryBackend project for isolated packaging and publishing.
"""

__version__ = "0.1.0"

from .interfaces import QueueMessage, NotificationPayload, QueueStats
from .sqs_client import SQSClient
from .notification_queue import NotificationQueueService

__all__ = [
    "__version__",
    "QueueMessage",
    "NotificationPayload",
    "QueueStats",
    "SQSClient",
    "NotificationQueueService",
]
