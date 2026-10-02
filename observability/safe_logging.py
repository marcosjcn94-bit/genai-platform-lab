import logging


class SafeLogFilter(logging.Filter):
    def filter(self, record):
        record.msg = "gateway_event"
        record.args = ()
        record.exc_info = None
        record.exc_text = None
        record.stack_info = None
        return True
