"""
error classes for kartograph
"""

class KartographError(Exception):
    """Base class for exceptions in this module."""
    pass
    
class KartographOptionParseError(KartographError):
    pass    


class KartographShapefileAttributesError(KartographError):
    pass
    
    
class KartographLayerSourceError(KartographError):
    pass