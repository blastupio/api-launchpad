from app.schema import TierInfo


bronze_tier = TierInfo(
    order=1,
    title="Bronze",
    blp_amount=2000,
)
silver_tier = TierInfo(
    order=2,
    title="Silver",
    blp_amount=5000,
)
gold_tier = TierInfo(
    order=3,
    title="Gold",
    blp_amount=10000,
)
titanium_tier = TierInfo(
    order=4,
    title="Titanium",
    blp_amount=20000,
)
platinum_tier = TierInfo(
    order=5,
    title="Platinum",
    blp_amount=50000,
)
diamond_tier = TierInfo(
    order=6,
    title="Diamond",
    blp_amount=100_000,
)
