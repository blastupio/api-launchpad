from dataclasses import dataclass


@dataclass(frozen=False)
class UserLockedAmount:
    native: float = 0
    stablecoin: float = 0


@dataclass(frozen=False)
class LockedAmount:
    native: float = 0
    stablecoin: float = 0
