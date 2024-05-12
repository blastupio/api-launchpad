from enum import Enum
from typing import NamedTuple
from typing_extensions import TypedDict


class BadgeType(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"
    BOOSTER = "BOOSTER"


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


class MunzenOrderType(str, Enum):
    ORDER_COMPLETE = "order_complete"
    ORDER_FAILED = "order_failed"


class MunzenWebhookEvent(TypedDict):
    eventType: MunzenOrderType
    orderId: str  # uuid
    blockchainNetworkTxId: str | None
    merchantOrderId: str | None
    customerId: str
    fromCurrency: str  # USD
    fromAmount: float
    fromAmountWithoutFees: float
    toCurrency: str  # NEAR
    toAmount: float
    toWallet: str
    exchangeRate: float
    providerFee: float
    networkFee: float
    networkFeeFiat: float
    createdAt: str  # iso format
    externalData: str  # json
