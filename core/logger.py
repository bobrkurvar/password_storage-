# import logging
# import sys
#
# logger = logging.getLogger()
# # logging.getLogger("aiogram").setLevel()
# logging.getLogger("asyncio").propagate = False
# logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter(
#     "[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s"
# )
#
# console_handler = logging.StreamHandler(sys.stdout)
# console_handler.setLevel(logging.DEBUG)
# console_handler.setFormatter(formatter)
#
# logger.addHandler(console_handler)

import logging
import sys

# class MyServicesFilter(logging.Filter):
#     def filter(self, record):
#         access = {"app", "bot", "aiogram", "main_app", "main_bot", "core", "shared"}
#         if record.levelno >= logging.WARNING:
#             return True
#         pocket = record.name.split(".")[0]
#         if pocket in access:
#             return True

class IgnoreFilter(logging.Filter):
    def filter(self, record):
        ignore = {"aiormq", "aio_pika", "asyncio"}
        if record.levelno >= logging.WARNING:
            return True
        pocket = record.name.split(".")[0]
        if pocket in ignore:
            return False
        return True

# class RabbitMQHandler(logging.Handler):
#     def __init__(self, queue_client, queue_name: str, service_name: str, env: str = 'dev'):
#         super().__init__()
#         self.queue_name = queue_name
#         self.environment = env
#         self.service_name = service_name
#         self.queue_client = queue_client
#
#     def emit(self, record: logging.LogRecord):
#         try:
#             metadata = getattr(record, "event_metadata", None)
#             event = dict(
#                 message=record.getMessage(),
#                 created_at=str(record.created),
#                 log_level=record.levelname,
#                 module_name=record.name,
#                 number_of_string=record.lineno,
#                 service_name=self.service_name,
#                 environment=self.environment,
#                 event_metadata=metadata  # можно добавить динамически
#             )
#             asyncio.create_task(self.queue_client.send_by_default_exchange(self.queue_name, event))
#         except Exception:
#             self.handleError(record)


def setup_logging(service_name: str = "", queue_client = None):
    logger = logging.getLogger()
    # if queue_client:
    #     rabbit_handler = RabbitMQHandler(queue_client, "logs_queue", service_name)
    #     rabbit_handler.setLevel(logging.DEBUG)
    #     if not any(isinstance(h, RabbitMQHandler) for h in logger.handlers):
    #         rabbit_handler.addFilter(MyServicesFilter())
    #         logger.addHandler(rabbit_handler)


    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        #console_handler.addFilter(IgnoreFilter())
        logger.addHandler(console_handler)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    logger.addFilter(IgnoreFilter())
