staking_abi = [
    {
        "type": "constructor",
        "inputs": [
            {"name": "_launchpad", "type": "address", "internalType": "address"},
            {"name": "_oracle", "type": "address", "internalType": "address"},
            {"name": "usdb", "type": "address", "internalType": "address"},
            {"name": "weth", "type": "address", "internalType": "address"},
        ],
        "stateMutability": "nonpayable",
    },
    {"type": "receive", "stateMutability": "payable"},
    {
        "type": "function",
        "name": "USDB",
        "inputs": [],
        "outputs": [{"name": "", "type": "address", "internalType": "contract IERC20Rebasing"}],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "WETH",
        "inputs": [],
        "outputs": [{"name": "", "type": "address", "internalType": "contract IERC20Rebasing"}],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "balanceAndRewards",
        "inputs": [
            {"name": "targetToken", "type": "address", "internalType": "address"},
            {"name": "account", "type": "address", "internalType": "address"},
        ],
        "outputs": [
            {"name": "balance", "type": "uint256", "internalType": "uint256"},
            {"name": "rewards", "type": "uint256", "internalType": "uint256"},
        ],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "claimReward",
        "inputs": [
            {"name": "targetToken", "type": "address", "internalType": "address"},
            {"name": "rewardToken", "type": "address", "internalType": "address"},
            {"name": "rewardAmount", "type": "uint256", "internalType": "uint256"},
            {"name": "getETH", "type": "bool", "internalType": "bool"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "type": "function",
        "name": "decimalsUSDB",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint8", "internalType": "uint8"}],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "initialize",
        "inputs": [{"name": "_owner", "type": "address", "internalType": "address"}],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "type": "function",
        "name": "lastIndex",
        "inputs": [{"name": "targetToken", "type": "address", "internalType": "address"}],
        "outputs": [{"name": "", "type": "uint256", "internalType": "uint256"}],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "launchpad",
        "inputs": [],
        "outputs": [{"name": "", "type": "address", "internalType": "contract ILaunchpad"}],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "minTimeToWithdraw",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint256", "internalType": "uint256"}],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "minUSDBStakeValue",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint256", "internalType": "uint256"}],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "oracle",
        "inputs": [],
        "outputs": [{"name": "", "type": "address", "internalType": "contract IChainlinkOracle"}],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "oracleDecimals",
        "inputs": [],
        "outputs": [{"name": "", "type": "uint8", "internalType": "uint8"}],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "owner",
        "inputs": [],
        "outputs": [{"name": "", "type": "address", "internalType": "address"}],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "renounceOwnership",
        "inputs": [],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "type": "function",
        "name": "setMinTimeToWithdraw",
        "inputs": [{"name": "_minTimeToWithdraw", "type": "uint256", "internalType": "uint256"}],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "type": "function",
        "name": "setMinUSDBStakeValue",
        "inputs": [{"name": "_minUSDBStakeValue", "type": "uint256", "internalType": "uint256"}],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "type": "function",
        "name": "stake",
        "inputs": [
            {"name": "depositToken", "type": "address", "internalType": "address"},
            {"name": "amount", "type": "uint256", "internalType": "uint256"},
        ],
        "outputs": [],
        "stateMutability": "payable",
    },
    {
        "type": "function",
        "name": "stakingInfos",
        "inputs": [{"name": "", "type": "address", "internalType": "address"}],
        "outputs": [
            {"name": "totalSupplyScaled", "type": "uint256", "internalType": "uint256"},
            {"name": "lastIndex", "type": "uint256", "internalType": "uint256"},
        ],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "totalSupply",
        "inputs": [{"name": "targetToken", "type": "address", "internalType": "address"}],
        "outputs": [{"name": "", "type": "uint256", "internalType": "uint256"}],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "transferOwnership",
        "inputs": [{"name": "newOwner", "type": "address", "internalType": "address"}],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "type": "function",
        "name": "userInfo",
        "inputs": [
            {"name": "targetToken", "type": "address", "internalType": "address"},
            {"name": "user", "type": "address", "internalType": "address"},
        ],
        "outputs": [
            {
                "name": "",
                "type": "tuple",
                "internalType": "struct YieldStaking.StakingUser",
                "components": [
                    {"name": "balanceScaled", "type": "uint256", "internalType": "uint256"},
                    {"name": "lockedBalance", "type": "uint256", "internalType": "uint256"},
                    {"name": "remainders", "type": "uint256", "internalType": "uint256"},
                    {"name": "timestampToWithdraw", "type": "uint256", "internalType": "uint256"},
                ],
            }
        ],
        "stateMutability": "view",
    },
    {
        "type": "function",
        "name": "withdraw",
        "inputs": [
            {"name": "targetToken", "type": "address", "internalType": "address"},
            {"name": "amount", "type": "uint256", "internalType": "uint256"},
            {"name": "getETH", "type": "bool", "internalType": "bool"},
        ],
        "outputs": [],
        "stateMutability": "nonpayable",
    },
    {
        "type": "event",
        "name": "Initialized",
        "inputs": [
            {"name": "version", "type": "uint64", "indexed": False, "internalType": "uint64"}
        ],
        "anonymous": False,
    },
    {
        "type": "event",
        "name": "OwnershipTransferred",
        "inputs": [
            {
                "name": "previousOwner",
                "type": "address",
                "indexed": True,
                "internalType": "address",
            },
            {"name": "newOwner", "type": "address", "indexed": True, "internalType": "address"},
        ],
        "anonymous": False,
    },
    {
        "type": "event",
        "name": "RewardClaimed",
        "inputs": [
            {
                "name": "stakingToken",
                "type": "address",
                "indexed": False,
                "internalType": "address",
            },
            {"name": "user", "type": "address", "indexed": True, "internalType": "address"},
            {"name": "rewardToken", "type": "address", "indexed": False, "internalType": "address"},
            {
                "name": "amountInStakingToken",
                "type": "uint256",
                "indexed": False,
                "internalType": "uint256",
            },
        ],
        "anonymous": False,
    },
    {
        "type": "event",
        "name": "Staked",
        "inputs": [
            {
                "name": "stakingToken",
                "type": "address",
                "indexed": False,
                "internalType": "address",
            },
            {"name": "user", "type": "address", "indexed": True, "internalType": "address"},
            {"name": "amount", "type": "uint256", "indexed": False, "internalType": "uint256"},
        ],
        "anonymous": False,
    },
    {
        "type": "event",
        "name": "StakingCreated",
        "inputs": [
            {"name": "stakingToken", "type": "address", "indexed": False, "internalType": "address"}
        ],
        "anonymous": False,
    },
    {
        "type": "event",
        "name": "Withdrawn",
        "inputs": [
            {
                "name": "stakingToken",
                "type": "address",
                "indexed": False,
                "internalType": "address",
            },
            {"name": "user", "type": "address", "indexed": True, "internalType": "address"},
            {"name": "amount", "type": "uint256", "indexed": False, "internalType": "uint256"},
        ],
        "anonymous": False,
    },
    {
        "type": "error",
        "name": "AddressEmptyCode",
        "inputs": [{"name": "target", "type": "address", "internalType": "address"}],
    },
    {
        "type": "error",
        "name": "AddressInsufficientBalance",
        "inputs": [{"name": "account", "type": "address", "internalType": "address"}],
    },
    {"type": "error", "name": "FailedInnerCall", "inputs": []},
    {"type": "error", "name": "InvalidInitialization", "inputs": []},
    {
        "type": "error",
        "name": "InvalidPool",
        "inputs": [{"name": "token", "type": "address", "internalType": "address"}],
    },
    {"type": "error", "name": "MathOverflowedMulDiv", "inputs": []},
    {"type": "error", "name": "NotInitializing", "inputs": []},
    {
        "type": "error",
        "name": "OwnableInvalidOwner",
        "inputs": [{"name": "owner", "type": "address", "internalType": "address"}],
    },
    {
        "type": "error",
        "name": "OwnableUnauthorizedAccount",
        "inputs": [{"name": "account", "type": "address", "internalType": "address"}],
    },
    {
        "type": "error",
        "name": "SafeERC20FailedOperation",
        "inputs": [{"name": "token", "type": "address", "internalType": "address"}],
    },
]
STAKING_USER_INFO_ABI = {
    "inputs": [
        {"internalType": "address", "name": "targetToken", "type": "address"},
        {"internalType": "address", "name": "user", "type": "address"},
    ],
    "name": "userInfo",
    "outputs": [
        {
            "components": [
                {"internalType": "uint256", "name": "balanceScaled", "type": "uint256"},
                {"internalType": "uint256", "name": "lockedBalance", "type": "uint256"},
                {"internalType": "uint256", "name": "remainders", "type": "uint256"},
                {"internalType": "uint256", "name": "timestampToWithdraw", "type": "uint256"},
            ],
            "internalType": "struct YieldStaking.StakingUser",
            "name": "",
            "type": "tuple",
        }
    ],
    "stateMutability": "view",
    "type": "function",
}
