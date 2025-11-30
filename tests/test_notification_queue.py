import json

from inventory_notifications.notification_queue import NotificationQueueService
from inventory_notifications.interfaces import NotificationPayload


class DummySQSClient:
    def __init__(self):
        self.sent = []

    def send_message(self, queue_name, body, delay_seconds=0):
        # emulate success
        self.sent.append((queue_name, body, delay_seconds))
        return True


def test_queue_notification_uses_sqs_client():
    sqs = DummySQSClient()
    svc = NotificationQueueService(sqs_client=sqs)
    payload = NotificationPayload(recipient_email="a@b.com", subject="Hello", message="world")
    assert svc.queue_notification(payload) is True
    assert len(sqs.sent) == 1
    queue_name, body, delay = sqs.sent[0]
    # body should be JSON string and contain a payload.notification key
    parsed = json.loads(body)
    assert parsed.get("payload") is not None
    assert parsed["payload"].get("notification") is not None
