import aio_pika
from core import conf
import json

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queue = None

    async def connect(self, queue_name: str):
        try:
            if self.connection is None:
                self.connection = await aio_pika.connect_robust(
                    f"amqp://guest:guest@{conf.queue_host}/"
                )

            if self.channel is None:
                self.channel = await self.connection.channel()

            await self.channel.declare_queue(queue_name, durable=True)
            return True
        except Exception:
            return False

    async def send_by_default_exchange(self, queue_name: str, data: dict):
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(data).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            ),
            routing_key=queue_name
        )

    async def close(self):
        if self.channel:
            await self.channel.close()
        if self.connect:
            await self.connection.close()