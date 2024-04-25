from app.schema import TierInfo, ChainId
from app.services.tiers.consts import (
    bronze_tier,
    silver_tier,
    gold_tier,
    titanium_tier,
    platinum_tier,
    diamond_tier,
)


def get_user_tier(blp_balance_by_chain_id: dict[ChainId, int]) -> TierInfo | None:
    total_balance = sum(blp_balance_by_chain_id.values()) or 0
    assert total_balance >= 0
    if 0 <= total_balance < bronze_tier.blp_amount:
        return None
    elif bronze_tier.blp_amount <= total_balance < silver_tier.blp_amount:
        return bronze_tier
    elif silver_tier.blp_amount <= total_balance < gold_tier.blp_amount:
        return silver_tier
    elif gold_tier.blp_amount <= total_balance < titanium_tier.blp_amount:
        return gold_tier
    elif titanium_tier.blp_amount <= total_balance < platinum_tier.blp_amount:
        return titanium_tier
    elif platinum_tier.blp_amount <= total_balance < diamond_tier.blp_amount:
        return platinum_tier
    elif total_balance >= diamond_tier.blp_amount:
        return diamond_tier
