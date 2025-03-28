from airflow.notifications.basenotifier import BaseNotifier
from airflow.utils.context import Context


class BreweryNotifier(BaseNotifier):
    template_fields = ("message",)

    def __init__(self, message):
        self.message = message

    @staticmethod
    def brewery_notifier(message: str) -> None:
        print(message)

    def notify(self, context: Context):
        title = f"Task {context['task_instance'].task_id} failed"
        self.brewery_notifier(f"{title}: {self.message}")
