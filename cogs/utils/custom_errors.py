from discord.ext.commands import CheckFailure


class MissingRequiredRole(CheckFailure):
    def __init__(self, message):
        self.message = message 
    def __str__(self):
        return self.message


class NoDiceGenerated(CheckFailure): pass
class NoCurrencySet(CheckFailure): pass
