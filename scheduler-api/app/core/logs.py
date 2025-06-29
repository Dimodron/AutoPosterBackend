import logging
from os import environ
import sys
import traceback
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
from typing import Optional

class LoggerService:
    """
    LoggerService provides a centralized logging interface for the application.
    It configures the standard Python logger and integrates with Sentry for error
    tracking and performance monitoring. When SENTRY_DSN is set, it initializes
    the Sentry SDK with a logging integration that captures INFO+ as breadcrumbs
    and sends ERROR+ events to Sentry.

    Methods:
        init(): Initialize Sentry SDK if DSN is provided.
        debug(msg): Log a debug-level message.
        info(msg): Log an info-level message.
        warning(msg): Log a warning-level message.
        error(msg, exc=None): Log an error message; capture exception to Sentry if provided and flush.
        critical(msg, exc=None): Log a critical message; capture to Sentry and flush.
    """


    _logger = None
    _sentry_initialized = False

    @staticmethod
    def init():

        if LoggerService._sentry_initialized:
            return
        dsn = environ.get("SENTRY_DSN")
        if not dsn:
            return

        debug_mode = environ.get("SENTRY_DEBUG", "false").lower() in ("1", "true", "yes")
        environment = environ.get("SENTRY_ENV", "production")

        sentry_logging = LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        )
        sentry_sdk.init(
            dsn=dsn,
            integrations=[sentry_logging],
            default_integrations=True,
            environment=environment,
            traces_sample_rate=float(environ.get("SENTRY_TRACES_SAMPLE_RATE", 0.0)),
            send_default_pii=True,
            debug=debug_mode,
            before_send=LoggerService._before_send
        )
        LoggerService._sentry_initialized = True

    @staticmethod
    def _before_send(event, hint):
        if event.get('logger') != 'custom-log' :
            return event
            
        return None

    @staticmethod
    def _get_logger():
        LoggerService.init()
        if LoggerService._logger:
            return LoggerService._logger

        logger = logging.getLogger("custom-log")
        log_level = environ.get("LOG_LEVEL", "INFO").upper()
        logger.setLevel(getattr(logging, log_level, logging.INFO))

        formatter = logging.Formatter(
            "\n%(asctime)s | %(levelname)s | %(message)s"
        )

        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        LoggerService._logger = logger
        return logger

    @staticmethod
    def debug(msg: str):
        LoggerService._get_logger().debug(msg)

    @staticmethod
    def info(msg: str):
        LoggerService._get_logger().info(msg)

    @staticmethod
    def warning(msg: str):
        LoggerService._get_logger().warning(msg)

    @staticmethod
    def error(msg: str, exc: Optional[Exception] = None):
        logger = LoggerService._get_logger()
        base_msg = msg

        if exc:
            tb_list = traceback.extract_tb(exc.__traceback__)
            parts = [f"Caused by --> {type(exc).__name__}: {exc}"]
            for tb in tb_list:
                parts.append(f"\nFile \"{tb.filename}\", line {tb.lineno}, in {tb.name}")
            base_msg = "\n" + "\n".join(parts)

            sentry_sdk.capture_exception(exc)
            sentry_sdk.flush(timeout=2.0)
        else:
            sentry_sdk.capture_message(msg, level="error")
            sentry_sdk.flush(timeout=2.0)

        logger.error(base_msg)

    @staticmethod
    def critical(msg: str, exc: Optional[Exception] = None):
        logger = LoggerService._get_logger()

        if exc:
            sentry_sdk.capture_exception(exc)
            sentry_sdk.flush(timeout=2.0)
        else:
            sentry_sdk.capture_message(msg, level="fatal")
            sentry_sdk.flush(timeout=2.0)

        logger.critical(msg)
