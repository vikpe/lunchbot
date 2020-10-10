from unittest import IsolatedAsyncioTestCase, mock

from freezegun import freeze_time

from main import LunchBot
from test_helpers import MockMessage, MockChannel


class LunchBotTestCase(IsolatedAsyncioTestCase):
    bot: LunchBot

    async def asyncSetUp(self):
        self.bot = LunchBot()

    async def test_send_test_message(self):
        message = MockMessage("!testlunch")
        await self.bot.on_message(message)

        message.author.send.assert_called_once_with(self.bot.lunch_message)

    @mock.patch("main.LunchBot.get_channel")
    async def test_send_lunch_message(self, mock_get_channel):
        mock_lunch_channel = MockChannel()
        mock_get_channel.return_value = mock_lunch_channel

        message = MockMessage("!lunch")
        await self.bot.on_message(message)

        mock_lunch_channel.send.assert_called_once_with(self.bot.lunch_message)

    async def test_send_announcements(self):
        message = MockMessage("!announcements")
        await self.bot.on_message(message)

        self.assertEqual(message.author.send.call_count, 2)
        message.author.send.assert_has_calls(
            [
                mock.call("Announcements are False"),
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

    async def test_should_send_lunch_message(self):
        from datetime import datetime, timedelta, date
        import os

        # annonucements disabled
        os.environ["ANNOUNCEMENTS"] = "0"
        self.assertFalse(await self.bot.should_send_lunch_message())

        # annonucements enabled
        os.environ["ANNOUNCEMENTS"] = "1"

        # already annonuced today
        self.bot.last_announcement_date = date.today()
        self.assertFalse(await self.bot.should_send_lunch_message())

        # set annonucement date to yesterday
        yesterdays_date = (datetime.now() - timedelta(1)).date()
        self.bot.last_announcement_date = yesterdays_date

        # not a working day
        with freeze_time("2020-01-04"):
            self.assertFalse(await self.bot.should_send_lunch_message())

        # working day
        with freeze_time("2020-01-03 08:00", tz_offset=-1) as frozen_time:
            # not time for announcement
            self.assertFalse(await self.bot.should_send_lunch_message())

            # finally, time for announcement!
            frozen_time.tick(3600)
            self.assertTrue(await self.bot.should_send_lunch_message())
