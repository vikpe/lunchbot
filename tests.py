from main import LunchBot

from unittest import IsolatedAsyncioTestCase, mock
from test_helpers import MockMessage


class LunchBotTestCase(IsolatedAsyncioTestCase):
    bot: LunchBot

    async def asyncSetUp(self):
        self.bot = LunchBot()

    async def test_send_test_message(self):
        message = MockMessage("!testlunch")
        await self.bot.on_message(message)

        message.author.send.assert_called_once_with(self.bot.lunch_message)

    async def test_send_announcements(self):
        message = MockMessage("!announcements")
        await self.bot.on_message(message)

        self.assertEqual(message.author.send.call_count, 2)
        message.author.send.assert_has_calls(
            [
                mock.call("Announcements are None"),
                mock.call("This can be changed in the Heroku Config Vars"),
            ]
        )

    async def test_ow_message__any(self):
        all_chars = [
            char
            for char_class in self.bot.config["ow_char_classes"].values()
            for char in char_class
        ]

        for i in range(1, 5):
            message = MockMessage("!ow")
            await self.bot.on_message(message)

            bot_channel_response = message.channel.send.call_args.args[0]
            self.assertIn(bot_channel_response, all_chars)

    async def test_ow_message__char_class(self):
        for i in range(1, 5):
            message = MockMessage("!ow support")
            await self.bot.on_message(message)

            bot_channel_response = message.channel.send.call_args.args[0]
            self.assertIn(
                bot_channel_response, self.bot.config["ow_char_classes"]["support"]
            )
