import asyncio
import json
import logging
import os
import random
from datetime import date
from datetime import datetime

import discord
import pytz


class LunchBotConfig:
    TIMEZONE = "Europe/Stockholm"
    ANNOUNCEMENT_HOUR = 9
    CHANNEL_ID = 540608386299985940  # Highly Unprofessional / lunch


def setup_logging():
    logger = logging.getLogger("discord")
    logger.setLevel(logging.WARNING)
    handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    )
    logger.addHandler(handler)


class LunchBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # init stuff
        self.lunch_message = ""
        self.config = ""
        self.ow_tanks = ""
        self.ow_damage = ""
        self.ow_support = ""
        self.last_announcement_date = ""
        self.announcements_enabled = os.getenv("ANNOUNCEMENTS")

        # create the background task and run it
        self.bg_task = self.loop.create_task(self.background_task())

    async def read_config(self):
        self.lunch_message = ""
        with open("config.json") as json_data_file:
            self.config = json.load(json_data_file)

        # read lunch options
        for option in self.config["options"]:
            self.lunch_message += option["emoji"] + " " + option["votingOption"] + "\n"

        # read ow characters
        self.ow_tanks = self.config["owTanks"]
        self.ow_damage = self.config["owDamage"]
        self.ow_support = self.config["owSupport"]

    async def write_config(self):
        print("Writing config data")
        print(self.config)
        with open("config.json", "w") as outfile:
            json.dump(self.config, outfile)
        print("Done")

    async def on_ready(self):
        await self.read_config()
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print("Announcements are " + str(self.announcements_enabled))
        print("------")

    async def on_message(self, message):
        if message.content == "!lunch":
            await self.send_lunch_message()
        elif message.content == "!testlunch":
            await self.send_test_message(message)
        elif message.content == "!announcements":
            await self.get_announcements(message)
        elif message.content == "!owtank":
            await self.send_owtank_message(message)
        elif message.content == "!owdps":
            await self.send_owdamage_message(message)
        elif message.content == "!owheal":
            await self.send_owsupport_message(message)
        elif message.content == "!owsupport":
            await self.send_owsupport_message(message)
        elif message.content == "!ow":
            await self.send_ow_message(message)

    async def send_lunch_message(self):
        channel = self.get_channel(LunchBotConfig.CHANNEL_ID)
        await channel.send(self.lunch_message)

    async def send_test_message(self, message=None):
        await message.author.send(self.lunch_message)

    async def get_announcements(self, message):
        self.announcements_enabled = os.getenv("ANNOUNCEMENTS")
        await message.author.send(
            "Announcements are " + str(self.announcements_enabled)
        )
        await message.author.send("This can be changed in the Heroku Config Vars")

    async def send_owtank_message(self, message):
        await message.channel.send(random.choice(self.ow_tanks))

    async def send_owdamage_message(self, message):
        await message.channel.send(random.choice(self.ow_damage))

    async def send_owsupport_message(self, message):
        await message.channel.send(random.choice(self.ow_support))

    async def send_ow_message(self, message):
        all_heroes = self.ow_tanks + self.ow_damage + self.ow_support
        await message.channel.send(random.choice(all_heroes))

    async def background_task(self):
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

                if todays_date != self.last_announcement_date:
                    # check if it's time to send the voting message
                    datetime_stockholm = datetime.now(
                        pytz.timezone(LunchBotConfig.TIMEZONE)
                    )

                    print("Checking weekday and hour")
                    is_workingday = datetime_stockholm.weekday() < 5
                    is_time_for_announcement = (
                        datetime_stockholm.hour == LunchBotConfig.ANNOUNCEMENT_HOUR
                    )

                    if is_workingday and is_time_for_announcement:
                        print("Setting self.last_annoucement")
                        self.last_announcement_date = todays_date

                        print("Sending lunch message")
                        await self.send_lunch_message()

            print("Sleep for 60 seconds")
            await asyncio.sleep(60)  # task runs every 60 seconds


if __name__ == "__main__":
    setup_logging()

    bot = LunchBot()
    api_token = os.getenv("LUNCHBOT_TOKEN")
    bot.run(api_token)
