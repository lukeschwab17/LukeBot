# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# Pip
from jsoncodable import JSONCodable

# Local
from ._utils import extract_number

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ------------------------------------------------------- class: ChannelAboutData -------------------------------------------------------- #

class ChannelAboutData(JSONCodable):

    # ------------------------------------------------------------- Init ------------------------------------------------------------- #

    def __init__(
        self,
        d: dict,
        debug: bool = False
    ):
        self.description = d['description']['simpleText'] if 'description' in d else None
        self.view_count = extract_number(d['viewCountText']['simpleText'], debug=debug) if 'viewCountText' in d else None


# ---------------------------------------------------------------------------------------------------------------------------------------- #