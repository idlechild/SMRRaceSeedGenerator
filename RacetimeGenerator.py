import logging
import os
from os import system
from racetime_bot import Bot
from racetime_bot import RaceHandler
import ssl
from SMROptions import SMRException
from SMROptions import SMROptions
from DiscordGenerator import DiscordGeneratorBot
import SeedGenerator


class RacetimeGeneratorHandler(RaceHandler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.discordbot = None
        self.seed_rolled = False


    def set_discord_bot(self, discordbot):
        self.discordbot = discordbot


    async def begin(self):
        await self.send_message("Coming Soon\u2122")


    async def error(self, data):
        if self.discordbot:
            self.discordbot.external_send_message_to_sandbox("RacetimeGeneratorHandler error: %s" % data.get('errors'))
        raise Exception(data.get('errors'))


    async def validate_can_roll_seed(self):
        if self.seed_rolled:
            raise SMRException("Seed already rolled for this raceroom")
        if self.data.get('status').get('value') in ('pending', 'in_progress'):
            raise SMRException("Cannot roll seed, race already in progress")


    async def generate_smvaria(self, options, settingsPreset, skillsPreset):
        await self.send_message("Generating seed...")
        settingsDict = {}
        seed = await SeedGenerator.generate_smvaria_seed(options, settingsPreset, skillsPreset, True, settingsDict)
        await self.set_bot_raceinfo(f"{settingsPreset} / {skillsPreset} - {seed.url}")
        await self.send_message(seed.url)
        warnings = await SeedGenerator.parse_smvaria_warnings(seed)
        for warning in warnings:
            await self.send_message(warning)
        self.seed_rolled = True


    async def ex_sgl23smr(self, args, message):
        try:
            options = SMROptions(args)
            if options.help:
                raise SMRException("!sgl23smr takes no arguments, but you can throw in the --beta option to roll the seed using the VARIA beta service.")
            options.validate_argument_count(0, 0, "0 expected")
            await self.validate_can_roll_seed()
            await self.generate_smvaria(options, "SGL23Online", "Season_Races")
        except SMRException as ce:
            await self.send_message(ce.message)
        except Exception as e:
            if self.discordbot:
                await self.discordbot.send_exception_to_sandbox(e)
            else:
                raise e


    async def ex_smrbot(self, args, message):
        try:
            options = SMROptions(args)
            options.validate_argument_count(0, 0, "0 expected")
            await self.send_message("Online")
        except SMRException as ce:
            await self.send_message(ce.message)
        except Exception as e:
            if self.discordbot:
                await self.discordbot.send_exception_to_sandbox(e)
            else:
                raise e


class RacetimeGeneratorBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        self.discordbot = None


    def set_discord_bot(self, discordbot):
        self.discordbot = discordbot


    def start_racetime_bot(self):
        self.loop.create_task(self.reauthorize())
        self.loop.create_task(self.refresh_races())


    def get_handler_class(self):
        return RacetimeGeneratorHandler


    def create_handler(self, race_data):
        handler = super().create_handler(race_data)
        handler.set_discord_bot(self.discordbot)
        return handler


racetimebot = None


def racetime_create_bot():
    global racetimebot
    clientId = os.environ.get("SMR_RACETIME_CLIENT_ID")
    clientSecret = os.environ.get("SMR_RACETIME_CLIENT_SECRET")
    if not clientId:
        if clientSecret:
            raise SMRException("SMR Race Seed Generator SMR_RACETIME_CLIENT_ID not set!")
    elif not clientSecret:
        raise SMRException("SMR Race Seed Generator SMR_RACETIME_CLIENT_SECRET not set!")
    else:
        racetimebot = RacetimeGeneratorBot(
            category_slug="smr",
            client_id=clientId,
            client_secret=clientSecret,
            logger=logging.getLogger()
        )
    return racetimebot


async def racetime_start_bot(racetimebot, discordbot):
    try:
        if discordbot:
            await discordbot.get_ready_event().wait()
        racetimebot.set_discord_bot(discordbot)
        racetimebot.start_racetime_bot()
    except Exception as e:
        if discordbot:
            await discordbot.send_exception_to_sandbox(e)
        else:
            raise e

