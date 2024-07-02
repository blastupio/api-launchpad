LAUNCHPAD_CONTRACT_ADDRESS_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "_weth", "type": "address"},
            {"internalType": "address", "name": "_usdb", "type": "address"},
            {"internalType": "address", "name": "_oracle", "type": "address"},
            {"internalType": "address", "name": "_yieldStaking", "type": "address"},
        ],
        "stateMutability": "nonpayable",
        "type": "constructor",
    },
    {
        "inputs": [{"internalType": "address", "name": "target", "type": "address"}],
        "name": "AddressEmptyCode",
        "type": "error",
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "AddressInsufficientBalance",
        "type": "error",
    },
    {"inputs": [], "name": "ECDSAInvalidSignature", "type": "error"},
    {
        "inputs": [{"internalType": "uint256", "name": "length", "type": "uint256"}],
        "name": "ECDSAInvalidSignatureLength",
        "type": "error",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "s", "type": "bytes32"}],
        "name": "ECDSAInvalidSignatureS",
        "type": "error",
    },
    {"inputs": [], "name": "FailedInnerCall", "type": "error"},
    {"inputs": [], "name": "InvalidInitialization", "type": "error"},
    {
        "inputs": [{"internalType": "uint256", "name": "id", "type": "uint256"}],
        "name": "InvalidSaleStatus",
        "type": "error",
    },
    {"inputs": [], "name": "NotInitializing", "type": "error"},
    {
        "inputs": [{"internalType": "address", "name": "owner", "type": "address"}],
        "name": "OwnableInvalidOwner",
        "type": "error",
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "OwnableUnauthorizedAccount",
        "type": "error",
    },
    {
        "inputs": [{"internalType": "address", "name": "token", "type": "address"}],
        "name": "SafeERC20FailedOperation",
        "type": "error",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "internalType": "uint64", "name": "version", "type": "uint64"}
        ],
        "name": "Initialized",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "previousOwner",
                "type": "address",
            },
            {"indexed": True, "internalType": "address", "name": "newOwner", "type": "address"},
        ],
        "name": "OwnershipTransferred",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "token", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "id", "type": "uint256"},
        ],
        "name": "TokenPlaced",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "token", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "buyer", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "id", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "amount", "type": "uint256"},
        ],
        "name": "TokensBought",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "token", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "id", "type": "uint256"},
            {"indexed": False, "internalType": "address", "name": "user", "type": "address"},
        ],
        "name": "TokensClaimed",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "user", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "token", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "id", "type": "uint256"},
            {
                "indexed": False,
                "internalType": "enum LaunchpadDataTypes.UserTiers",
                "name": "tier",
                "type": "uint8",
            },
        ],
        "name": "UserRegistered",
        "type": "event",
    },
    {
        "inputs": [],
        "name": "USDB",
        "outputs": [{"internalType": "contract IERC20", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "WETH",
        "outputs": [{"internalType": "contract IERC20", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "address", "name": "paymentContract", "type": "address"},
            {"internalType": "uint256", "name": "volume", "type": "uint256"},
            {"internalType": "address", "name": "receiver", "type": "address"},
            {"internalType": "bytes", "name": "signature", "type": "bytes"},
        ],
        "name": "buyTokens",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "id", "type": "uint256"}],
        "name": "claimRemainders",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "id", "type": "uint256"}],
        "name": "claimTokens",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "decimalsUSDB",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "address", "name": "user", "type": "address"},
        ],
        "name": "getClaimableAmount",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "id", "type": "uint256"}],
        "name": "getPlacedToken",
        "outputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "price", "type": "uint256"},
                    {"internalType": "uint256", "name": "volumeForYieldStakers", "type": "uint256"},
                    {"internalType": "uint256", "name": "volume", "type": "uint256"},
                    {
                        "internalType": "uint256",
                        "name": "initialVolumeForLowTiers",
                        "type": "uint256",
                    },
                    {
                        "internalType": "uint256",
                        "name": "initialVolumeForHighTiers",
                        "type": "uint256",
                    },
                    {"internalType": "uint256", "name": "lowTiersWeightsSum", "type": "uint256"},
                    {"internalType": "uint256", "name": "highTiersWeightsSum", "type": "uint256"},
                    {"internalType": "address", "name": "addressForCollected", "type": "address"},
                    {"internalType": "uint256", "name": "registrationStart", "type": "uint256"},
                    {"internalType": "uint256", "name": "registrationEnd", "type": "uint256"},
                    {"internalType": "uint256", "name": "publicSaleStart", "type": "uint256"},
                    {"internalType": "uint256", "name": "fcfsSaleStart", "type": "uint256"},
                    {"internalType": "uint256", "name": "saleEnd", "type": "uint256"},
                    {"internalType": "uint256", "name": "tgeStart", "type": "uint256"},
                    {"internalType": "uint256", "name": "vestingStart", "type": "uint256"},
                    {"internalType": "uint256", "name": "vestingDuration", "type": "uint256"},
                    {"internalType": "uint8", "name": "tokenDecimals", "type": "uint8"},
                    {"internalType": "uint8", "name": "tgePercent", "type": "uint8"},
                    {"internalType": "bool", "name": "approved", "type": "bool"},
                    {"internalType": "address", "name": "token", "type": "address"},
                ],
                "internalType": "struct LaunchpadDataTypes.PlacedToken",
                "name": "",
                "type": "tuple",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "id", "type": "uint256"}],
        "name": "getStatus",
        "outputs": [
            {"internalType": "enum LaunchpadDataTypes.SaleStatus", "name": "", "type": "uint8"}
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "_owner", "type": "address"},
            {"internalType": "address", "name": "_signer", "type": "address"},
            {"internalType": "address", "name": "_operator", "type": "address"},
            {"internalType": "address", "name": "_points", "type": "address"},
            {"internalType": "address", "name": "_pointsOperator", "type": "address"},
        ],
        "name": "initialize",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "enum LaunchpadDataTypes.UserTiers", "name": "", "type": "uint8"}
        ],
        "name": "minAmountForTier",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "operator",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "oracle",
        "outputs": [{"internalType": "contract IChainlinkOracle", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "oracleDecimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "owner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "price", "type": "uint256"},
                    {"internalType": "uint256", "name": "volumeForYieldStakers", "type": "uint256"},
                    {"internalType": "uint256", "name": "volume", "type": "uint256"},
                    {
                        "internalType": "uint256",
                        "name": "initialVolumeForLowTiers",
                        "type": "uint256",
                    },
                    {
                        "internalType": "uint256",
                        "name": "initialVolumeForHighTiers",
                        "type": "uint256",
                    },
                    {"internalType": "uint256", "name": "lowTiersWeightsSum", "type": "uint256"},
                    {"internalType": "uint256", "name": "highTiersWeightsSum", "type": "uint256"},
                    {"internalType": "address", "name": "addressForCollected", "type": "address"},
                    {"internalType": "uint256", "name": "registrationStart", "type": "uint256"},
                    {"internalType": "uint256", "name": "registrationEnd", "type": "uint256"},
                    {"internalType": "uint256", "name": "publicSaleStart", "type": "uint256"},
                    {"internalType": "uint256", "name": "fcfsSaleStart", "type": "uint256"},
                    {"internalType": "uint256", "name": "saleEnd", "type": "uint256"},
                    {"internalType": "uint256", "name": "tgeStart", "type": "uint256"},
                    {"internalType": "uint256", "name": "vestingStart", "type": "uint256"},
                    {"internalType": "uint256", "name": "vestingDuration", "type": "uint256"},
                    {"internalType": "uint8", "name": "tokenDecimals", "type": "uint8"},
                    {"internalType": "uint8", "name": "tgePercent", "type": "uint8"},
                    {"internalType": "bool", "name": "approved", "type": "bool"},
                    {"internalType": "address", "name": "token", "type": "address"},
                ],
                "internalType": "struct LaunchpadDataTypes.PlacedToken",
                "name": "_placedToken",
                "type": "tuple",
            }
        ],
        "name": "placeTokens",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "placedTokens",
        "outputs": [
            {"internalType": "uint256", "name": "price", "type": "uint256"},
            {"internalType": "uint256", "name": "volumeForYieldStakers", "type": "uint256"},
            {"internalType": "uint256", "name": "volume", "type": "uint256"},
            {"internalType": "uint256", "name": "initialVolumeForLowTiers", "type": "uint256"},
            {"internalType": "uint256", "name": "initialVolumeForHighTiers", "type": "uint256"},
            {"internalType": "uint256", "name": "lowTiersWeightsSum", "type": "uint256"},
            {"internalType": "uint256", "name": "highTiersWeightsSum", "type": "uint256"},
            {"internalType": "address", "name": "addressForCollected", "type": "address"},
            {"internalType": "uint256", "name": "registrationStart", "type": "uint256"},
            {"internalType": "uint256", "name": "registrationEnd", "type": "uint256"},
            {"internalType": "uint256", "name": "publicSaleStart", "type": "uint256"},
            {"internalType": "uint256", "name": "fcfsSaleStart", "type": "uint256"},
            {"internalType": "uint256", "name": "saleEnd", "type": "uint256"},
            {"internalType": "uint256", "name": "tgeStart", "type": "uint256"},
            {"internalType": "uint256", "name": "vestingStart", "type": "uint256"},
            {"internalType": "uint256", "name": "vestingDuration", "type": "uint256"},
            {"internalType": "uint8", "name": "tokenDecimals", "type": "uint8"},
            {"internalType": "uint8", "name": "tgePercent", "type": "uint8"},
            {"internalType": "bool", "name": "approved", "type": "bool"},
            {"internalType": "address", "name": "token", "type": "address"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "enum LaunchpadDataTypes.UserTiers", "name": "tier", "type": "uint8"},
            {"internalType": "uint256", "name": "amountOfTokens", "type": "uint256"},
            {"internalType": "bytes", "name": "signature", "type": "bytes"},
        ],
        "name": "register",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "enum LaunchpadDataTypes.UserTiers", "name": "tier", "type": "uint8"},
            {"internalType": "uint256", "name": "amountOfTokens", "type": "uint256"},
            {"internalType": "bytes", "name": "signature", "type": "bytes"},
            {"internalType": "bytes", "name": "approveSignature", "type": "bytes"},
        ],
        "name": "registerWithApprove",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "renounceOwnership",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "uint256", "name": "_fcfsSaleStart", "type": "uint256"},
        ],
        "name": "setFCFSSaleStart",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256[6]", "name": "amounts", "type": "uint256[6]"}],
        "name": "setMinAmountsForTiers",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "_operator", "type": "address"}],
        "name": "setOperator",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "uint256", "name": "_publicSaleStart", "type": "uint256"},
        ],
        "name": "setPublicSaleStart",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "uint256", "name": "_registrationEnd", "type": "uint256"},
        ],
        "name": "setRegistrationEnd",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "uint256", "name": "_registrationStart", "type": "uint256"},
        ],
        "name": "setRegistrationStart",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "uint256", "name": "_saleEnd", "type": "uint256"},
        ],
        "name": "setSaleEnd",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "_signer", "type": "address"}],
        "name": "setSigner",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "uint256", "name": "_tgeStart", "type": "uint256"},
        ],
        "name": "setTgeStart",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "uint256", "name": "_vestingStart", "type": "uint256"},
        ],
        "name": "setVestingStart",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256[6]", "name": "weights", "type": "uint256[6]"}],
        "name": "setWeightsForTiers",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "signer",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "address", "name": "newOwner", "type": "address"}],
        "name": "transferOwnership",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "address", "name": "user", "type": "address"},
        ],
        "name": "userAllowedAllocation",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "id", "type": "uint256"},
            {"internalType": "address", "name": "user", "type": "address"},
        ],
        "name": "userInfo",
        "outputs": [
            {
                "components": [
                    {"internalType": "uint256", "name": "claimedAmount", "type": "uint256"},
                    {"internalType": "uint256", "name": "boughtAmount", "type": "uint256"},
                    {"internalType": "uint256", "name": "boughtPublicSale", "type": "uint256"},
                    {
                        "internalType": "enum LaunchpadDataTypes.UserTiers",
                        "name": "tier",
                        "type": "uint8",
                    },
                    {"internalType": "bool", "name": "registered", "type": "bool"},
                ],
                "internalType": "struct LaunchpadDataTypes.User",
                "name": "",
                "type": "tuple",
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "", "type": "uint256"},
            {"internalType": "address", "name": "", "type": "address"},
        ],
        "name": "users",
        "outputs": [
            {"internalType": "uint256", "name": "claimedAmount", "type": "uint256"},
            {"internalType": "uint256", "name": "boughtAmount", "type": "uint256"},
            {"internalType": "uint256", "name": "boughtPublicSale", "type": "uint256"},
            {"internalType": "enum LaunchpadDataTypes.UserTiers", "name": "tier", "type": "uint8"},
            {"internalType": "bool", "name": "registered", "type": "bool"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "enum LaunchpadDataTypes.UserTiers", "name": "", "type": "uint8"}
        ],
        "name": "weightForTier",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "yieldStaking",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
]
