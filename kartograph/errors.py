"""
error classes for kartograph
"""


class KartographError(Exception):
    """Base class for exceptions in this module."""
    def __str__(self):
        return '\033[0;31;40mKartograph-Error:\033[0m ' + super(KartographError, self).__str__()


class KartographOptionParseError(KartographError):
    pass


class KartographShapefileAttributesError(KartographError):
    pass


class KartographLayerSourceError(KartographError):
    pass
