import asyncio
import os
from os import system
from DiscordGenerator import discord_create_bot
from DiscordGenerator import discord_start_bot
from RacetimeGenerator import racetime_create_bot
from RacetimeGenerator import racetime_start_bot


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    discordbot = discord_create_bot()
    if discordbot:
        loop.create_task(discord_start_bot(discordbot))
    racetimebot = racetime_create_bot()
    if racetimebot:
        loop.create_task(racetime_start_bot(racetimebot, discordbot))
    if discordbot or racetimebot:
        loop.run_forever()

