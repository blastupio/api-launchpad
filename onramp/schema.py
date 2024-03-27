from typing import Literal

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    ok: bool = Field(default=False)
    error: str


class OnRampPayload(BaseModel):
    recipient: str = Field(pattern="^(0x)[0-9a-fA-F]{40}$")
    amount: str
    currency: Literal['ETH'] = Field(default="ETH")


class OnRampResponseData(BaseModel):
    internal_uuid: str
    link: str


class OnRampResponse(BaseModel):
    ok: bool
    data: OnRampResponseData


class OnrampOrderResponseData(BaseModel):
    order_id: str = Field(alias="orderId")
    blockchain_network_tx_id: str | None = Field(alias="blockchainNetworkTxId", default=None)
    merchant_order_id: str = Field(alias="merchantOrderId")
    customer_id: str = Field(alias="customerId")
    from_currency: str = Field(alias="fromCurrency")
    from_amount: float | int = Field(alias="fromAmount")
    from_amount_without_fees: float | int = Field(alias="fromAmountWithoutFees")
    to_currency: str = Field(alias="toCurrency")
    to_amount: float | int = Field(alias="toAmount")
    to_wallet: str = Field(alias="toWallet")
    exchange_rate: float | int = Field(alias="exchangeRate")
    provider_fee: float | int = Field(alias="providerFee")
    network_fee: float | int = Field(alias="networkFee")
    network_fee_fiat: float | int = Field(alias="networkFeeFiat")
    status: str
    created_at: str = Field(alias="createdAt")


class OnrampOrderResponse(BaseModel):
    ok: bool
    data: OnrampOrderResponseData
