import os
import discord
import asyncio
import logging
import datetime

logger = logging.getLogger('discord')
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.background_task())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        self.last_lunch_message_sent = datetime.datetime(
            datetime.MINYEAR, 1, 1, 0, 0)

    async def on_message(self, message):
        if message.content.startswith('!lunch'):
            time_delta = datetime.datetime.now() - self.last_lunch_message_sent
            if time_delta.days > 0 or time_delta.seconds >= 12 * 60 * 60:
                self.last_lunch_message_sent = datetime.datetime.now()
                channel = self.get_channel(540608386299985940)
                await channel.send("""
:white_check_mark: Ja
:no_entry: Nej
<:mk:541268624392978442> Matkultur
:hot_pepper: Chili & Lime
:pizza: La Fontana 
:house: Husman
:sushi: Yatai
:green_salad: Brödernas
:golf: Golfen
:office: Collegium
:cityscape: LPS
:grey_question:  Annat, kommentera!""")
            else:
                await message.author.send("DOOF! Lunchvote redan uppe.")

    async def send_lunch_message(self):
        channel = self.get_channel(540608386299985940)
        await channel.send("Hello :)")

    async def background_task(self):
        await self.wait_until_ready()

        while not self.is_closed():
            # check if it's time to send the voting message
            if datetime.datetime.now().weekday() < 8: # and datetime.datetime.now().hour == 9:
                self.send_lunch_message()

            await asyncio.sleep(60) # task runs every 60 seconds

client = MyClient()
api_token = os.getenv("LUNCHBOT_TOKEN")

client.run(api_token)
