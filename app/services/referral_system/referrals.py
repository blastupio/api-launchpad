from app.dependencies import ProfileCrudDep
from app.services.referral_system.cache import referral_redis


async def get_n_referrals(address: str, profile_crud: ProfileCrudDep):
    cached_n_referrals = await referral_redis.get_n_referrals(address)
    if cached_n_referrals is not None:
        return cached_n_referrals

    n_referrals = await profile_crud.count_referrals(referrer=address)
    await referral_redis.set_n_referrals(address, n_referrals)
    return n_referrals
