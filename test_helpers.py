from unittest import mock


class SendableMixin(mock.AsyncMock):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.send = mock.AsyncMock()


class MockAuthor(SendableMixin):
    pass


class MockChannel(SendableMixin):
    pass


class MockMessage(mock.AsyncMock):
    def __init__(self, content, **kwargs):
        super().__init__(**kwargs)
        self.content = content
        self.author = kwargs.get("author", MockAuthor())
        self.channel = kwargs.get("channel", MockChannel())
