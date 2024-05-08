from enum import Enum
from typing import NamedTuple


class BadgeType(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


class PlacedToken(NamedTuple):
    price: int  # in wei
    volumeForYieldStakers: int  # in wei
    volume: int  # in wei
    initialVolumeForLowTiers: int  # in wei
    initialVolumeForHighTiers: int  # in wei
    lowTiersWeightsSum: int
    highTiersWeightsSum: int
    addressForCollected: str
    registrationStart: int  # unix timestamp
    registrationEnd: int  # unix timestamp
    publicSaleStart: int  # unix timestamp
    fcfsSaleStart: int  # unix timestamp
    saleEnd: int  # unix timestamp
    tgeStart: int  # unix timestamp
    vestingStart: int  # unix timestamp
    vestingDuration: int
    tokenDecimals: int
    tgePercent: int
    approved: bool
    token: str


class ProjectIdWithRaised(NamedTuple):
    project_id: str
    raised: float
