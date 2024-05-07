from enum import Enum
from typing_extensions import TypedDict


class BadgeType(str, Enum):
    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"


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
