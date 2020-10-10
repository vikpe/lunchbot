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
        self.announcements_enabled = os.getenv("ANNOUNCEMENTS")

    @property
    def lunch_message(self) -> str:
        options_as_array_of_strings = [
            option["emoji"] + " " + option["label"]
            for option in self.config["lunch_options"]
        ]
        separator = "\n"
        return separator.join(options_as_array_of_strings)

    async def write_config(self):
        print("Writing config data")
        print(self.config)
        with open("config.json", "w") as outfile:
            json.dump(self.config, outfile)
        print("Done")

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
        message_char_class = message.content.strip(f" {self.CMD_OW}")

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

    async def lunch_task(self):
        print("Entering background_task")
        await self.wait_until_ready()

        print("Checking not self.is_closed")
        while not self.is_closed():
            # check if announcements are enabled
            print("Checking self.announcements")
            if self.announcements_enabled:
                # check if we already sent a message today
                print("Checking self.last_announcement_date")
                todays_date = date.today()
                has_announced_today = todays_date == self.last_announcement_date

                if not has_announced_today:
                    # check if it's time to send the voting message
                    timezone = pytz.timezone(self.config["timezone"])
                    current_datetime = datetime.now(timezone)

                    print("Checking weekday and hour")
                    is_workingday = current_datetime.weekday() < 5
                    is_time_for_announcement = (
                        current_datetime.hour == self.config["lunch_announcement_hour"]
                    )

                    if is_workingday and is_time_for_announcement:
                        print("Setting self.last_annoucement")
                        self.last_announcement_date = todays_date

                        print("Sending lunch message")
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
