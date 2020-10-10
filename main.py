import asyncio
import json
import logging
import os
import random
from datetime import date
from datetime import datetime

import discord
import pytz


class LunchBot(discord.Client):
    CMD_OW = "!ow"
    CMD_LUNCH = "!lunch"
    CMD_TEST_LUNCH = "!testlunch"
    CMD_ANNOUNCEMENTS = "!announcements"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        with open("config.json") as json_data_file:
            self.config = json.load(json_data_file)

        self.last_announcement_date = ""

    @property
    def lunch_message(self) -> str:
        options_formatted = [
            option["emoji"] + " " + option["label"]
            for option in self.config["lunch_options"]
        ]
        separator = "\n"
        return separator.join(options_formatted)

    @property
    def announcements_enabled(self):
        return bool(int(os.getenv("ANNOUNCEMENTS", 0)))

    async def on_ready(self):
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print("Announcements are " + str(self.announcements_enabled))
        print("------")
        self.loop.create_task(self.lunch_task())

    async def on_message(self, message):
        if message.content == self.CMD_LUNCH:
            await self.send_lunch_message()
        elif message.content == self.CMD_TEST_LUNCH:
            await self.send_test_message(message)
        elif message.content == self.CMD_ANNOUNCEMENTS:
            await self.send_announcements(message)
        elif message.content.startswith(self.CMD_OW):
            await self.send_ow_message(message)

    async def send_lunch_message(self):
        channel = self.get_channel(self.config["lunch_channel_id"])
        await channel.send(self.lunch_message)

    async def send_test_message(self, message=None):
        await message.author.send(self.lunch_message)

    async def send_announcements(self, message):
        self.announcements_enabled = os.getenv("ANNOUNCEMENTS")
        await message.author.send(
            "Announcements are " + str(self.announcements_enabled)
        )
        await message.author.send("This can be changed in the Heroku Config Vars")

    async def send_ow_message(self, message):
        # eg get "tank" from "!ow tank"
        message_char_class = message.content.strip(f"{self.CMD_OW} ")

        if message_char_class in self.config["ow_char_classes"].keys():
            chars_to_choose_from = self.config["ow_char_classes"][message_char_class]
        else:
            all_chars = [
                char
                for char_class in self.config["ow_char_classes"].values()
                for char in char_class
            ]
            chars_to_choose_from = all_chars

        random_char = random.choice(chars_to_choose_from)
        await message.channel.send(random_char)

    async def should_send_lunch_message(self):
        # announcement enabled?
        if not self.announcements_enabled:
            return False

        # already announced?
        has_announced_today = date.today() == self.last_announcement_date

        if has_announced_today:
            return False

        # working day?
        timezone = pytz.timezone(self.config["timezone"])
        current_datetime = datetime.now(timezone)

        is_workingday = current_datetime.weekday() < 5

        if not is_workingday:
            return False

        # time for announcement?
        is_time_for_announcement = (
            current_datetime.hour == self.config["lunch_announcement_hour"]
        )

        return is_time_for_announcement

    async def lunch_task(self):
        print("Entering background_task")
        await self.wait_until_ready()

        print("Checking not self.is_closed")
        while not self.is_closed():
            if await self.should_send_lunch_message():
                await self.send_lunch_message()

            print("Sleep for 60 seconds")
            await asyncio.sleep(60)  # task runs every 60 seconds


def setup_logging():
    logger = logging.getLogger("discord")
    logger.setLevel(logging.WARNING)
    handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    )
    logger.addHandler(handler)


if __name__ == "__main__":
    setup_logging()

    bot = LunchBot()
    api_token = os.getenv("LUNCHBOT_TOKEN")
    bot.run(api_token)
