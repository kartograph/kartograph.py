"""
error classes for kartograph
"""


class KartographError(Exception):
    """Base class for exceptions in this module."""
    def __str__(self):
        return 'Kartograph-Error: ' + super(KartographError, self).__str__()


class KartographOptionParseError(KartographError):
    pass


class KartographShapefileAttributesError(KartographError):
    pass


class KartographLayerSourceError(KartographError):
    pass
