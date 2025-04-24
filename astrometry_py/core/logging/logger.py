import logging
import sys
from .notifier import Notifier

class NotifierHandler(logging.Handler):
    """
    A logging handler that pushes log records out via a Notifier.
    """
    def __init__(self, notifier: Notifier, level: int = logging.ERROR):
        super().__init__(level)
        self.notifier = notifier
        self.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            self.notifier.notify(msg)
        except Exception:
            self.handleError(record)


class Logger:
    """
    A basic logger class that logs to stdout, optionally to a file,
    and can notify via Slack/Discord/Email through Notifier.
    """
    def __init__(self,
                 name: str,
                 level: int = logging.INFO,
                 logfile: str | None = None,
                 notifier_channels: int | None = None,
                 notifier_level: int = logging.ERROR):
        # --- Standard logger setup ---
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False

        fmt = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
        formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(level)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        if logfile:
            fh = logging.FileHandler(logfile)
            fh.setLevel(level)
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

        # --- Notifier integration ---
        self.notifier = None
        if notifier_channels is not None:
            # Initialize your Notifier
            self.notifier = Notifier(notifier_channels)
            # Attach a handler that pushes out notifications on errors (or above)
            nh = NotifierHandler(self.notifier, level=notifier_level)
            self.logger.addHandler(nh)

    # Standard logging methods
    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

    # Shortcut for manual notifications
    def notify(self, msg: str):
        """
        Directly send a notification (via Slack/Discord/Email)
        even if no handler is attached.
        """
        if not self.notifier:
            raise RuntimeError("Notifier not configured on this Logger")
        self.notifier.notify(msg)
