import json
import os
from os import system
from pyz3r.smvaria import SuperMetroidVaria
from SMROptions import SMRException
from SMROptions import SMROptions


class VariaGenerator(SuperMetroidVaria):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.debugdefaults = False
        self.debugsettings = False
        self.debugskills = False


    async def get_default_settings(self):
        settings = await super().get_default_settings()
        if self.debugdefaults:
            debug_text = self.debug_settings_to_text(settings)
            raise SMRException("VariaGenerator Defaults:\n%s" % debug_text)
        return settings


    async def get_settings(self):
        settings = await super().get_settings()
        if self.debugsettings:
            debug_text = self.debug_settings_to_text(settings)
            raise SMRException("VariaGenerator Settings:\n%s" % debug_text)
        elif self.debugskills:
            debug_text = self.debug_skills_to_text(settings["paramsFileTarget"], "")
            raise SMRException("VariaGenerator Skills:\n%s" % debug_text)
        return settings


    def debug_settings_to_text(self, settings):
        debug_text = ""
        for key, value in sorted(settings.items()):
            if key != "paramsFileTarget":
                debug_text += "%s: %s\n" % (key, value)
            elif not self.debugskills:
                debug_text += "%s: %s\n" % (key, self.settings_preset)
            else:
                debug_text += "%s: {\n" % key
                debug_text += self.debug_skills_to_text(value, "        ")
                debug_text += "}\n"
        return debug_text


    def debug_skills_to_text(self, skills, indent):
        debug_text = ""
        debug_skills_data = json.loads(skills)
        for key, value in sorted(debug_skills_data.items()):
            if not isinstance(value, dict):
                debug_text += "%s%s: %s\n" % (indent, key, value)
            else:
                debug_text += "%s%s: {\n" % (indent, key)
                for k, v in sorted(value.items()):
                    debug_text += "%s        %s: %s\n" % (indent, k, v)
                debug_text += "%s}\n" % indent
        return debug_text


async def validate_choozo_params(split, area, boss, difficulty, escape, morph, start):
    if split not in ['FullCountdown', 'M/m', 'RandomSplit']:
        raise SMRException("Invalid item split setting.  Must be FullCountdown, M/m or RandomSplit.")

    if area not in ['FullArea', 'LightArea', 'VanillaArea']:
        raise SMRException("Invalid area setting.  Must be FullArea, LightArea or VanillaArea.")

    if boss not in ['RandomBoss', 'VanillaBoss']:
        raise SMRException("Invalid boss setting.  Must be RandomBoss or VanillaBoss.")

    if difficulty not in ['VeryHardDifficulty', 'HarderDifficulty', 'HardDifficulty', 'MediumDifficulty', 'EasyDifficulty', 'BasicDifficulty']:
        raise SMRException("Invalid difficulty setting.  Must be VeryHardDifficulty, HarderDifficulty, HardDifficulty, MediumDifficulty, EasyDifficulty or BasicDifficulty.")

    if escape not in ['RandomEscape', 'VanillaEscape']:
        raise SMRException("Invalid escape setting.  Must be RandomEscape or VanillaEscape.")

    if morph not in ['LateMorph', 'RandomMorph', 'EarlyMorph']:
        raise SMRException("Invalid morph setting.  Must be LateMorph, RandomMorph or EarlyMorph.")

    if start not in ['DeepStart', 'RandomStart', 'NotDeepStart', 'ShallowStart', 'VanillaStart']:
        raise SMRException("Invalid start setting.  Must be DeepStart, RandomStart, NotDeepStart, ShallowStart or VanillaStart.")


async def generate_choozo_seed(options, race, split, area, boss, difficulty, escape, morph, start):
    splitDict = {
        "FullCountdown": "FullWithHUD",
        "M/m": "Major",
        "RandomSplit": "random"
    }

    difficultyDict = {
        "VeryHardDifficulty": "harder",
        "HarderDifficulty": "harder",
        "HardDifficulty": "hard",
        "MediumDifficulty": "medium",
        "EasyDifficulty": "easy",
        "BasicDifficulty": "easy"
    }

    morphDict = {
        "LateMorph": "late",
        "RandomMorph": "random",
        "EarlyMorph": "early"
    }

    startDict = {
        "DeepStart": [
            'Aqueduct',
            'Bubble Mountain',
            'Firefleas Top'
        ],
        "RandomStart": [
            'Aqueduct',
            'Big Pink',
            'Bubble Mountain',
            'Business Center',
            'Etecoons Supers',
            'Firefleas Top',
            'Gauntlet Top',
            'Golden Four',
            'Green Brinstar Elevator',
            'Red Brinstar Elevator',
            'Wrecked Ship Main'
        ],
        "NotDeepStart": [
            'Big Pink',
            'Business Center',
            'Etecoons Supers',
            'Gauntlet Top',
            'Golden Four',
            'Green Brinstar Elevator',
            'Red Brinstar Elevator',
            'Wrecked Ship Main'
        ],
        "ShallowStart": [
            'Big Pink',
            'Gauntlet Top',
            'Green Brinstar Elevator',
            'Wrecked Ship Main'
        ],
        "VanillaStart": [
            'Landing Site'
        ]
    }

    settingsPreset = "Season_Races"
    skillsPreset = "newbie" if difficulty == "BasicDifficulty" else "Season_Races"
    settingsDict = {
        "hud": "on",
        "suitsRestriction": "off",
        "variaTweaks": "on",

        "majorsSplit": splitDict[split],
        "majorsSplitMultiSelect": ['FullWithHUD', 'Major'],

        "areaRandomization": "full" if area == "FullArea" else "light" if area == "LightArea" else "off",
        "areaLayout": "off" if area == "VanillaArea" else "on",

        "bossRandomization": "off" if boss == "VanillaBoss" else "on",

        "maxDifficulty": difficultyDict[difficulty],

        "escapeRando": "off" if escape == "VanillaEscape" else "on",

        "morphPlacement": morphDict[morph],

        "startLocation": "Landing Site" if start == "VanillaStart" else "random",
        "startLocationMultiSelect": startDict[start]
    }

    return await generate_smvaria_seed(options, settingsPreset, skillsPreset, race, settingsDict)


async def generate_smvaria_seed(options, settingsPreset, skillsPreset, race, settingsDict):
    seed = await VariaGenerator.create(
        baseurl="https://variabeta.pythonanywhere.com" if options.beta else "https://randommetroidsolver.pythonanywhere.com",
        settings_preset=settingsPreset,
        skills_preset=skillsPreset,
        race=race,
        settings_dict=settingsDict,
        raise_for_status=False
    )

    if not hasattr(seed, 'guid'):
        raise SMRException("Error: %s" % seed.data)

    return seed


async def parse_smvaria_warnings(seed):
    warnings = []
    errorMsg = seed.data.get('errorMsg', '')
    if len(errorMsg) > 0:
        warnings = errorMsg.replace("<br/>", "\n").rstrip().split('\n')
    return warnings

