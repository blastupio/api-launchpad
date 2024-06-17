from web3 import Web3

from app.schema import TierInfo

bronze_tier = TierInfo(
    order=1,
    title="Bronze",
    blp_amount=Web3.to_wei(2_000, "ether"),
)
silver_tier = TierInfo(
    order=2,
    title="Silver",
    blp_amount=Web3.to_wei(5_000, "ether"),
)
gold_tier = TierInfo(
    order=3,
    title="Gold",
    blp_amount=Web3.to_wei(10_000, "ether"),
)
titanium_tier = TierInfo(
    order=4,
    title="Titanium",
    blp_amount=Web3.to_wei(20_000, "ether"),
)
platinum_tier = TierInfo(
    order=5,
    title="Platinum",
    blp_amount=Web3.to_wei(50_000, "ether"),
)
diamond_tier = TierInfo(
    order=6,
    title="Diamond",
    blp_amount=Web3.to_wei(100_000, "ether"),
)
