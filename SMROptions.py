import os
from os import system


class SMRException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__("SMRException")


class SMROptions():
    def __init__(self, args):
        self.args = list(args)
        self.beta = False
        self.help = False
        self.parse_args()


    def parse_args(self):
        i = 0
        while i < len(self.args):
            if self.args[i].startswith('--'):
                self.parse_option(self.args[i][2:])
                del self.args[i]
            elif self.args[i].startswith('-'):
                self.parse_option(self.args[i][1:])
                del self.args[i]
            else:
                ++i


    def parse_option(self, option):
        option_lowercase = option.lower()
        if "beta" == option_lowercase:
            self.beta = True
        elif "help" == option_lowercase or "?" == option_lowercase:
            self.help = True
        else:
            raise SMRException("Error: Option %s not supported, try --help if you need assistance" % option)


    def validate_argument_count(self, minArgs, maxArgs, argsDescription):
        if (len(self.args) < minArgs) or ((maxArgs >= 0) and (len(self.args) > maxArgs)):
            argumentsProvided = "%s %s provided" % (len(self.args), "argument" if 1 == len(self.args) else "arguments")
            raise SMRException("%s, %s" % (argumentsProvided, argsDescription))

