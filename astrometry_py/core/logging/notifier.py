class Notifier:
    SLACK   = 1 << 0  # 0b001
    DISCORD = 1 << 1  # 0b010
    EMAIL   = 1 << 2  # 0b100

    def __init__(self, channels: int):
        self._channels = channels
        # fixme: webhook ID and whatever logic here

    def notify(self, msg: str):
        if self._channels & Notifier.SLACK:
            self._notify_slack(msg)
        if self._channels & Notifier.DISCORD:
            self._notify_discord(msg)
        if self._channels & Notifier.EMAIL:
            self._notify_email(msg)

    def debug(self, msg: str):
        self.notify(msg)

    def info(self, msg: str):
        self.notify(msg)

    def warning(self, msg: str):
        self.notify(msg)

    def error(self, msg: str):
        self.notify(msg)

    def critical(self, msg: str):
        self.notify(msg)

    def _notify_slack(self, msg: str):
        print(f"[Slack] {msg}")

    def _notify_discord(self, msg: str):
        print(f"[Discord] {msg}")

    def _notify_email(self, msg: str):
        print(f"[Email] {msg}")


    def notify(self, msg: str):
        """Send `msg` to whichever channels were enabled."""
        if self._channels & Notifier.SLACK:
            self._notify_slack(msg)
        if self._channels & Notifier.DISCORD:
            self._notify_discord(msg)
        if self._channels & Notifier.EMAIL:
            self._notify_email(msg)

    def _notify_slack(self, msg: str):
        print(f"[Slack] {msg}")

    def _notify_discord(self, msg: str):
        print(f"[Discord] {msg}")

    def _notify_email(self, msg: str):
        print(f"[Email] {msg}")