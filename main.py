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
            if time_delta.seconds >= 12 * 60 * 60:
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


client = MyClient()
api_token = os.getenv("LUNCHBOT_TOKEN")

client.run(api_token)
