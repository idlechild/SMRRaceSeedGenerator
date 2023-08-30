import asyncio
import datetime
import discord
from discord.ext import commands
import os
from os import system
import traceback
from SMROptions import SMRException
from SMROptions import SMROptions
import SeedGenerator


class DiscordGeneratorBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.exceptionrecursion = False
        self.readyevent = asyncio.Event()
        self.roles = None
        self.roles_channel = None
        self.sandbox_channel = None
        self.seeds_channel = None


    async def generate_choozo(self, ctx, options, race, split, area, boss, difficulty, escape, morph, start, title):
        await SeedGenerator.validate_choozo_params(split, area, boss, difficulty, escape, morph, start)
        await self.send_message_to_channel(ctx, "Generating seed...")
        seed = await SeedGenerator.generate_choozo_seed(options, race, split, area, boss, difficulty, escape, morph, start)

        splitDescriptionDict = {
            "FullCountdown": "Full Countdown",
            "M/m": "Major/minor",
            "RandomSplit": "Random"
        }

        if difficulty == "VeryHardDifficulty":
            difficulty = "Very HardDifficulty"

        if start == "NotDeepStart":
            start = "Not DeepStart"

        embedTitle = "%s\n%s Seed" % (
            "Generated Super Metroid SMR" if len(title) == 0 else ' '.join(title),
            "Race" if race else "Practice"
        )
        embedDescription = (
            f"**Item Split: **{splitDescriptionDict[split]}\n"
            f"**Area: **{area[:-4]}\n"
            f"**Boss: **{boss[:-4]}\n"
            f"**Difficulty: **{difficulty[:-10]}\n"
            f"**Escape: **{escape[:-6]}\n"
            f"**Morph: **{morph[:-5]}\n"
            f"**Start: **{start[:-5]}"
        )
        await self.embed_seed(ctx, seed, embedTitle, embedDescription)


    async def generate_smvaria(self, ctx, options, settingsPreset, skillsPreset):
        await self.send_message_to_channel(ctx, "Generating seed...")
        settingsDict = {}
        seed = await SeedGenerator.generate_smvaria_seed(options, settingsPreset, skillsPreset, True, settingsDict)
        embedTitle = "Generated Super Metroid Race Seed"
        embedDescription = (
            f"**Settings: **{settingsPreset}\n"
            f"**Skills: **{skillsPreset}"
        )
        await self.embed_seed(ctx, seed, embedTitle, embedDescription)


    async def embed_seed(self, ctx, seed, embedTitle, embedDescription):
        embed = discord.Embed(
            title=embedTitle,
            description=embedDescription,
            color=discord.Colour.orange(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(
            name="Link",
            value=seed.url,
            inline=False
        )
        warnings = await SeedGenerator.parse_smvaria_warnings(seed)
        if len(warnings) > 0:
            embed.add_field(
                name="Warnings",
                value='\n'.join(warnings),
                inline=False
            )
        await ctx.send(embed=embed)


    async def validate_channel(self, ctx):
        if not isinstance(ctx.message.channel, discord.channel.DMChannel):
            if self.seeds_channel:
                if ctx.message.channel.id != self.seeds_channel and ctx.message.channel.id != self.sandbox_channel:
                    raise SMRException("Please go to the appropriate channel to generate seeds")


    async def generate_choozo_parse_args(self, ctx, race, args):
        try:
            await self.validate_channel(ctx)
            options = SMROptions(args)
            if options.help:
                raise SMRException("%s takes seven arguments (item split, area, boss, difficulty, escape, morph, start)"
                                   " and an optional title (all arguments after the first seven are treated as a title).\n"
                                   "You can also throw in the --beta option to roll the seed using the VARIA beta service." % "!choozorace" if race else "!choozopractice")
            options.validate_argument_count(7, -1, "7 required (item split, area, boss, difficulty, escape, morph, start)")
            args = options.args
            await self.generate_choozo(ctx, options, race, options.args[0], options.args[1], options.args[2], options.args[3],
                                       options.args[4], options.args[5], options.args[6], options.args[7:])
        except SMRException as ce:
            await self.send_message_to_channel(ctx, ce.message)
        except Exception as e:
            await self.send_exception_to_sandbox(e)


    async def generate_sgl23smr_parse_args(self, ctx, args):
        try:
            await self.validate_channel(ctx)
            options = SMROptions(args)
            if options.help:
                raise SMRException("!sgl23smr takes no arguments, but you can throw in the --beta option to roll the seed using the VARIA beta service.")
            options.validate_argument_count(0, 0, "0 expected")
            await self.generate_smvaria(ctx, options, "SGL23Online", "Season_Races")
        except SMRException as ce:
            await self.send_message_to_channel(ctx, ce.message)
        except Exception as e:
            await self.send_exception_to_sandbox(e)


    async def smrbot_parse_args(self, ctx, args):
        try:
            await self.validate_channel(ctx)
            options = SMROptions(args)
            options.validate_argument_count(0, 0, "0 expected")
            await self.send_message_to_channel(ctx, "SMR Race Seed Generator online")
        except SMRException as ce:
            await self.send_message_to_channel(ctx, ce.message)
        except Exception as e:
            await self.send_exception_to_sandbox(e)


    async def generate_smvaria_parse_args(self, ctx, args):
        try:
            await self.validate_channel(ctx)
            options = SMROptions(args)
            if options.help:
                raise SMRException("!smvaria takes two arguments (settings preset, skills preset).\n"
                                   "You can also throw in the --beta option to roll the seed using the VARIA beta service.")
            options.validate_argument_count(2, 2, "2 required (settings preset, skills preset)")
            await self.generate_smvaria(ctx, options, options.args[0], options.args[1])
        except SMRException as ce:
            await self.send_message_to_channel(ctx, ce.message)
        except Exception as e:
            await self.send_exception_to_sandbox(e)


    async def handle_role_react(self, payload, add):
        try:
            if self.roles_channel and self.roles_channel == payload.channel_id:
                emojiDict = {
                    "🇦": "Async Race Admin",
                    "🇨": "Comms",
                    "🇵": "Practice",
                    "🇷": "Runner",
                    "🇹": "Tracking"
                }
                if payload.emoji.name in emojiDict:
                    reactRoleName = emojiDict[payload.emoji.name]
                    if self.roles is None:
                        self.roles = await self.guilds[0].fetch_roles()
                    for self.role in roles:
                        if self.role.name == reactRoleName:
                            if add:
                                await payload.member.add_roles(role)
                            else:
                                for member in self.get_all_members():
                                    if member.id == payload.user_id:
                                        await member.remove_roles(role)
        except Exception as e:
            await self.send_exception_to_sandbox(e)


    async def send_message_to_channel(self, channel, message):
        if not channel:
            raise SMRException("Request to send message to empty channel")
        if not message or 0 >= len(message):
            raise SMRException("Request to send empty message")
        while len(message) > 2000:
            await channel.send(message[:2000])
            message = message[2000:]
        if len(message) > 0:
            await channel.send(message)


    def external_send_message_to_sandbox(self, message):
        self.dispatch("send_message_to_sandbox", message)


    async def handle_send_message_to_sandbox(self, message):
        channel = self.get_channel(self.sandbox_channel)
        await self.send_message_to_channel(channel, message)


    async def send_exception_to_sandbox(self, e):
        formatted_exception = ''.join(traceback.format_exception(None, e, e.__traceback__))
        message = "SMR Race Seed Generator Exception:\n%s" % formatted_exception
        self.external_send_message_to_sandbox(message)
        raise e


    def handle_exception(self, loop, context):
        if not self.exceptionrecursion:
            self.exceptionrecursion = True
            message = "SMR Race Seed Generator Exception:\n%s" % context
            self.external_send_message_to_sandbox(context)
            self.exceptionrecursion = False


    async def handle_ready(self):
        asyncio.get_event_loop().set_exception_handler(self.handle_exception)
        await self.handle_send_message_to_sandbox("SMR Race Seed Generator started")
        self.readyevent.set()


    async def handle_message(self, message):
        ctx = await self.get_context(message)
        await self.invoke(ctx)


    def get_ready_event(self):
        return self.readyevent


discordbot = DiscordGeneratorBot(command_prefix="!", intents=discord.Intents.all())


@discordbot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def choozopractice(ctx, *args):
    await discordbot.generate_choozo_parse_args(ctx, False, args)


@discordbot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def choozorace(ctx, *args):
    await discordbot.generate_choozo_parse_args(ctx, True, args)


@discordbot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def sgl23smr(ctx, *args):
    await discordbot.generate_sgl23smr_parse_args(ctx, args)


@discordbot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def smrbot(ctx, *args):
    await discordbot.smrbot_parse_args(ctx, args)


@discordbot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def smvaria(ctx, *args):
    await discordbot.generate_smvaria_parse_args(ctx, args)


@discordbot.event
async def on_raw_reaction_add(payload):
    await discordbot.handle_role_react(payload, True)


@discordbot.event
async def on_raw_reaction_remove(payload):
    await discordbot.handle_role_react(payload, False)


@discordbot.event
async def on_send_message_to_sandbox(message):
    await discordbot.handle_send_message_to_sandbox(message)


@discordbot.event
async def on_ready():
    await discordbot.handle_ready()


@discordbot.event
async def on_message(message):
    await discordbot.handle_message(message)


def discord_create_bot():
    global discordbot
    return discordbot if os.environ.get("SMR_DISCORD_TOKEN") else None


async def discord_start_bot(discordbot):
    token = os.environ.get("SMR_DISCORD_TOKEN")
    if not token:
        raise SMRException("SMR Race Seed Generator SMR_DISCORD_TOKEN not set!")
    sandbox_channel = os.environ.get("SMR_DISCORD_SANDBOX_CHANNEL")
    if not sandbox_channel:
        raise SMRException("SMR Race Seed Generator SMR_DISCORD_SANDBOX_CHANNEL not set!")
    try:
        discordbot.sandbox_channel = int(sandbox_channel)
    except ValueError:
        raise SMRException("SMR Race Seed Generator SMR_DISCORD_SANDBOX_CHANNEL is not a 64-bit integer!")
    roles_channel = os.environ.get("SMR_DISCORD_ROLES_CHANNEL")
    if roles_channel:
        try:
            discordbot.roles_channel = int(roles_channel)
        except ValueError:
            raise SMRException("SMR Race Seed Generator SMR_DISCORD_ROLES_CHANNEL is not a 64-bit integer!")
    seeds_channel = os.environ.get("SMR_DISCORD_SEEDS_CHANNEL")
    if seeds_channel:
        try:
            discordbot.seeds_channel = int(seeds_channel)
        except ValueError:
            raise SMRException("SMR Race Seed Generator SMR_DISCORD_SEEDS_CHANNEL is not a 64-bit integer!")
    await discordbot.start(token)

