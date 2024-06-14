from app.schema import TierInfo
from app.services.tiers.consts import (
    bronze_tier,
    silver_tier,
    gold_tier,
    titanium_tier,
    platinum_tier,
    diamond_tier,
)


def get_user_tier(blp_staked_balance: int) -> TierInfo | None:
    assert blp_staked_balance >= 0
    if 0 <= blp_staked_balance < bronze_tier.blp_amount:
        return None
    elif bronze_tier.blp_amount <= blp_staked_balance < silver_tier.blp_amount:
        return bronze_tier
    elif silver_tier.blp_amount <= blp_staked_balance < gold_tier.blp_amount:
        return silver_tier
    elif gold_tier.blp_amount <= blp_staked_balance < titanium_tier.blp_amount:
        return gold_tier
    elif titanium_tier.blp_amount <= blp_staked_balance < platinum_tier.blp_amount:
        return titanium_tier
    elif platinum_tier.blp_amount <= blp_staked_balance < diamond_tier.blp_amount:
        return platinum_tier
    elif blp_staked_balance >= diamond_tier.blp_amount:
        return diamond_tier
