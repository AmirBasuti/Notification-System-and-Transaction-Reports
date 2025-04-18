from abc import ABC, abstractmethod


class NotificationMedium(ABC):
    def send(self, recipient, content, **kwargs):
        formatted = self.format_content(content, **kwargs)
        return self._send(recipient, formatted, **kwargs)

    @abstractmethod
    def _send(self, recipient, content, **kwargs):
        raise NotImplementedError("_send must be implemented in subclasses")

    def format_content(self, content, **kwargs):
        return content
