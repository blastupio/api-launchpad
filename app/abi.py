ERC20_ABI = [
    {
        "name": "approve",
        "inputs": [
            {
                "internalType": "address",
                "name": "spender",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "amount",
                "type": "uint256"
            }
        ],
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "mint",
        "payable": True,
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "name": "allowance",
        "inputs": [
            {
                "internalType": "address",
                "name": "owner",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "spender",
                "type": "address"
            }
        ],
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]
PRESALE_ABI = [
    {
        "type": "constructor",
        "name": "",
        "inputs": [
            {
                "type": "address",
                "name": "COIN_PRICE_FEED_",
                "internalType": "contract AggregatorV3Interface"
            },
            {
                "type": "address",
                "name": "usdcToken_",
                "internalType": "contract IERC20"
            },
            {
                "type": "address",
                "name": "usdtToken_",
                "internalType": "contract IERC20"
            },
            {
                "type": "address",
                "name": "protocolWallet_",
                "internalType": "address"
            },
            {
                "type": "address",
                "name": "admin",
                "internalType": "address"
            }
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "error",
        "name": "EnforcedPause",
        "inputs": [],
        "outputs": []
    },
    {
        "type": "error",
        "name": "ExpectedPause",
        "inputs": [],
        "outputs": []
    },
    {
        "type": "error",
        "name": "OwnableInvalidOwner",
        "inputs": [
            {
                "type": "address",
                "name": "owner",
                "internalType": "address"
            }
        ],
        "outputs": []
    },
    {
        "type": "error",
        "name": "OwnableUnauthorizedAccount",
        "inputs": [
            {
                "type": "address",
                "name": "account",
                "internalType": "address"
            }
        ],
        "outputs": []
    },
    {
        "type": "error",
        "name": "SafeTransferFailed",
        "inputs": [],
        "outputs": []
    },
    {
        "type": "error",
        "name": "SafeTransferFromFailed",
        "inputs": [],
        "outputs": []
    },
    {
        "type": "event",
        "name": "OwnershipTransferred",
        "inputs": [
            {
                "type": "address",
                "name": "previousOwner",
                "indexed": True,
                "internalType": "address"
            },
            {
                "type": "address",
                "name": "newOwner",
                "indexed": True,
                "internalType": "address"
            }
        ],
        "outputs": [],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "Paused",
        "inputs": [
            {
                "type": "address",
                "name": "account",
                "indexed": False,
                "internalType": "address"
            }
        ],
        "outputs": [],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "StageUpdated",
        "inputs": [
            {
                "type": "uint256",
                "name": "currentStage",
                "indexed": False,
                "internalType": "uint256"
            }
        ],
        "outputs": [],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "TokensBought",
        "inputs": [
            {
                "type": "address",
                "name": "token",
                "indexed": True,
                "internalType": "address"
            },
            {
                "type": "address",
                "name": "user",
                "indexed": True,
                "internalType": "address"
            },
            {
                "type": "address",
                "name": "referrer",
                "indexed": True,
                "internalType": "address"
            },
            {
                "type": "uint256",
                "name": "amount",
                "indexed": False,
                "internalType": "uint256"
            }
        ],
        "outputs": [],
        "anonymous": False
    },
    {
        "type": "event",
        "name": "Unpaused",
        "inputs": [
            {
                "type": "address",
                "name": "account",
                "indexed": False,
                "internalType": "address"
            }
        ],
        "outputs": [],
        "anonymous": False
    },
    {
        "type": "function",
        "name": "COIN_DECIMALS",
        "inputs": [],
        "outputs": [
            {
                "type": "uint8",
                "name": "",
                "internalType": "uint8"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "COIN_PRICE_FEED",
        "inputs": [],
        "outputs": [
            {
                "type": "address",
                "name": "",
                "internalType": "contract AggregatorV3Interface"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "PRICEFEED_DECIMALS",
        "inputs": [],
        "outputs": [
            {
                "type": "uint8",
                "name": "",
                "internalType": "uint8"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "STABLETOKEN_PRICE",
        "inputs": [],
        "outputs": [
            {
                "type": "int32",
                "name": "",
                "internalType": "int32"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "STABLE_TOKEN_DECIMALS",
        "inputs": [],
        "outputs": [
            {
                "type": "uint8",
                "name": "",
                "internalType": "uint8"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "balances",
        "inputs": [
            {
                "type": "address",
                "name": "user",
                "internalType": "address"
            }
        ],
        "outputs": [
            {
                "type": "uint256",
                "name": "balance",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "depositCoin",
        "inputs": [
            {
                "type": "address",
                "name": "referrer",
                "internalType": "address"
            }
        ],
        "outputs": [],
        "stateMutability": "payable"
    },
    {
        "type": "function",
        "name": "depositCoinTo",
        "inputs": [
            {
                "type": "address",
                "name": "to",
                "internalType": "address"
            },
            {
                "type": "address",
                "name": "referrer",
                "internalType": "address"
            }
        ],
        "outputs": [],
        "stateMutability": "payable"
    },
    {
        "type": "function",
        "name": "depositUSDC",
        "inputs": [
            {
                "type": "uint256",
                "name": "amount",
                "internalType": "uint256"
            },
            {
                "type": "address",
                "name": "referrer",
                "internalType": "address"
            }
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "depositUSDCTo",
        "inputs": [
            {
                "type": "address",
                "name": "to",
                "internalType": "address"
            },
            {
                "type": "uint256",
                "name": "amount",
                "internalType": "uint256"
            },
            {
                "type": "address",
                "name": "referrer",
                "internalType": "address"
            }
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "depositUSDT",
        "inputs": [
            {
                "type": "uint256",
                "name": "amount",
                "internalType": "uint256"
            },
            {
                "type": "address",
                "name": "referrer",
                "internalType": "address"
            }
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "depositUSDTTo",
        "inputs": [
            {
                "type": "address",
                "name": "to",
                "internalType": "address"
            },
            {
                "type": "uint256",
                "name": "amount",
                "internalType": "uint256"
            },
            {
                "type": "address",
                "name": "referrer",
                "internalType": "address"
            }
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "owner",
        "inputs": [],
        "outputs": [
            {
                "type": "address",
                "name": "",
                "internalType": "address"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "pause",
        "inputs": [],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "paused",
        "inputs": [],
        "outputs": [
            {
                "type": "bool",
                "name": "",
                "internalType": "bool"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "protocolWallet",
        "inputs": [],
        "outputs": [
            {
                "type": "address",
                "name": "",
                "internalType": "address"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "renounceOwnership",
        "inputs": [],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "setStage",
        "inputs": [
            {
                "type": "uint256",
                "name": "stageIterator_",
                "internalType": "uint256"
            }
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "stageIterator",
        "inputs": [],
        "outputs": [
            {
                "type": "uint256",
                "name": "",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "stages",
        "inputs": [
            {
                "type": "uint256",
                "name": "",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "type": "uint96",
                "name": "cost",
                "internalType": "uint96"
            },
            {
                "type": "uint160",
                "name": "amount",
                "internalType": "uint160"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "totalSoldInUSD",
        "inputs": [],
        "outputs": [
            {
                "type": "uint256",
                "name": "",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "totalTokensSold",
        "inputs": [],
        "outputs": [
            {
                "type": "uint256",
                "name": "",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "transferOwnership",
        "inputs": [
            {
                "type": "address",
                "name": "newOwner",
                "internalType": "address"
            }
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "unpause",
        "inputs": [],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "updateProtocolWallet",
        "inputs": [
            {
                "type": "address",
                "name": "wallet",
                "internalType": "address"
            }
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "updateTotalSold",
        "inputs": [
            {
                "type": "uint256",
                "name": "amount",
                "internalType": "uint256"
            }
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    },
    {
        "type": "function",
        "name": "usdcToken",
        "inputs": [],
        "outputs": [
            {
                "type": "address",
                "name": "",
                "internalType": "contract IERC20"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "usdtToken",
        "inputs": [],
        "outputs": [
            {
                "type": "address",
                "name": "",
                "internalType": "contract IERC20"
            }
        ],
        "stateMutability": "view"
    }
]
PRESALE_BSC_ABI = [{
    "inputs": [{
        "internalType": "contract AggregatorV3Interface",
        "name": "COIN_PRICE_FEED_",
        "type": "address"
    }, {"internalType": "contract IERC20", "name": "usdcToken_", "type": "address"}, {
        "internalType": "contract IERC20",
        "name": "usdtToken_",
        "type": "address"
    }, {"internalType": "address", "name": "protocolWallet_", "type": "address"}, {
        "internalType": "address",
        "name": "admin",
        "type": "address"
    }], "stateMutability": "nonpayable", "type": "constructor"
}, {"inputs": [], "name": "EnforcedPause", "type": "error"}, {
    "inputs": [],
    "name": "ExpectedPause",
    "type": "error"
}, {
    "inputs": [{"internalType": "address", "name": "owner", "type": "address"}],
    "name": "OwnableInvalidOwner",
    "type": "error"
}, {
    "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
    "name": "OwnableUnauthorizedAccount",
    "type": "error"
}, {"inputs": [], "name": "SafeTransferFailed", "type": "error"}, {
    "inputs": [],
    "name": "SafeTransferFromFailed",
    "type": "error"
}, {
    "anonymous": False,
    "inputs": [{
        "indexed": True,
        "internalType": "address",
        "name": "previousOwner",
        "type": "address"
    }, {"indexed": True, "internalType": "address", "name": "newOwner", "type": "address"}],
    "name": "OwnershipTransferred",
    "type": "event"
}, {
    "anonymous": False,
    "inputs": [{"indexed": False, "internalType": "address", "name": "account", "type": "address"}],
    "name": "Paused",
    "type": "event"
}, {
    "anonymous": False,
    "inputs": [{"indexed": False, "internalType": "uint256", "name": "currentStage", "type": "uint256"}],
    "name": "StageUpdated",
    "type": "event"
}, {
    "anonymous": False,
    "inputs": [{"indexed": True, "internalType": "address", "name": "token", "type": "address"}, {
        "indexed": True,
        "internalType": "address",
        "name": "user",
        "type": "address"
    }, {"indexed": True, "internalType": "address", "name": "referrer", "type": "address"}, {
                   "indexed": False,
                   "internalType": "uint256",
                   "name": "amount",
                   "type": "uint256"
               }],
    "name": "TokensBought",
    "type": "event"
}, {
    "anonymous": False,
    "inputs": [{"indexed": False, "internalType": "address", "name": "account", "type": "address"}],
    "name": "Unpaused",
    "type": "event"
}, {
    "inputs": [],
    "name": "COIN_PRICE_FEED",
    "outputs": [{"internalType": "contract AggregatorV3Interface", "name": "", "type": "address"}],
    "stateMutability": "view",
    "type": "function"
}, {
    "inputs": [],
    "name": "PRICEFEED_DECIMALS",
    "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
    "stateMutability": "view",
    "type": "function"
}, {
    "inputs": [],
    "name": "STABLETOKEN_PRICE",
    "outputs": [{"internalType": "int32", "name": "", "type": "int32"}],
    "stateMutability": "view",
    "type": "function"
}, {
    "inputs": [],
    "name": "TOKEN_PRECISION",
    "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
    "stateMutability": "view",
    "type": "function"
}, {
    "inputs": [{"internalType": "address", "name": "user", "type": "address"}],
    "name": "balances",
    "outputs": [{"internalType": "uint256", "name": "balance", "type": "uint256"}],
    "stateMutability": "view",
    "type": "function"
}, {
    "inputs": [{"internalType": "address", "name": "referrer", "type": "address"}],
    "name": "depositCoin",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
}, {
    "inputs": [{"internalType": "address", "name": "to", "type": "address"}, {
        "internalType": "address",
        "name": "referrer",
        "type": "address"
    }], "name": "depositCoinTo", "outputs": [], "stateMutability": "payable", "type": "function"
}, {
    "inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}, {
        "internalType": "address",
        "name": "referrer",
        "type": "address"
    }], "name": "depositUSDC", "outputs": [], "stateMutability": "nonpayable", "type": "function"
}, {
    "inputs": [{"internalType": "address", "name": "to", "type": "address"}, {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
    }, {"internalType": "address", "name": "referrer", "type": "address"}],
    "name": "depositUSDCTo",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
}, {
    "inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}, {
        "internalType": "address",
        "name": "referrer",
        "type": "address"
    }], "name": "depositUSDT", "outputs": [], "stateMutability": "nonpayable", "type": "function"
}, {
    "inputs": [{"internalType": "address", "name": "to", "type": "address"}, {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
    }, {"internalType": "address", "name": "referrer", "type": "address"}],
    "name": "depositUSDTTo",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
}, {
    "inputs": [],
    "name": "owner",
    "outputs": [{"internalType": "address", "name": "", "type": "address"}],
    "stateMutability": "view",
    "type": "function"
}, {"inputs": [], "name": "pause", "outputs": [], "stateMutability": "nonpayable", "type": "function"}, {
    "inputs": [],
    "name": "paused",
    "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
    "stateMutability": "view",
    "type": "function"
}, {
    "inputs": [],
    "name": "protocolWallet",
    "outputs": [{"internalType": "address", "name": "", "type": "address"}],
    "stateMutability": "view",
    "type": "function"
}, {
    "inputs": [],
    "name": "renounceOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
}, {
    "inputs": [{"internalType": "contract IERC20", "name": "token", "type": "address"}, {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
    }], "name": "rescueFunds", "outputs": [], "stateMutability": "nonpayable", "type": "function"
}, {
    "inputs": [{"internalType": "uint256", "name": "stageIterator_", "type": "uint256"}],
    "name": "setStage",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
}, {
    "inputs": [],
    "name": "stageIterator",
    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
    "stateMutability": "view",
    "type": "function"
}, {
    "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
    "name": "stages",
    "outputs": [{"internalType": "uint96", "name": "cost", "type": "uint96"}, {
        "internalType": "uint160",
        "name": "amount",
        "type": "uint160"
    }],
    "stateMutability": "view",
    "type": "function"
}, {
    "inputs": [],
    "name": "totalSoldInUSD",
    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
    "stateMutability": "view",
    "type": "function"
}, {
    "inputs": [],
    "name": "totalTokensSold",
    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
    "stateMutability": "view",
    "type": "function"
}, {
    "inputs": [{"internalType": "address", "name": "newOwner", "type": "address"}],
    "name": "transferOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
}, {
    "inputs": [],
    "name": "unpause",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
}, {
    "inputs": [{"internalType": "address", "name": "wallet", "type": "address"}],
    "name": "updateProtocolWallet",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
}, {
    "inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}],
    "name": "updateTotalSold",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
}, {
    "inputs": [],
    "name": "usdcToken",
    "outputs": [{"internalType": "contract IERC20", "name": "", "type": "address"}],
    "stateMutability": "view",
    "type": "function"
}, {
    "inputs": [],
    "name": "usdtToken",
    "outputs": [{"internalType": "contract IERC20", "name": "", "type": "address"}],
    "stateMutability": "view",
    "type": "function"
}]
PRICE_FEED_ABI = [{"type": "constructor", "name": "",
                   "inputs": [{"type": "address", "name": "_aggregator", "internalType": "address"},
                              {"type": "address", "name": "_accessController", "internalType": "address"}],
                   "outputs": [], "stateMutability": "nonpayable"}, {"type": "event", "name": "AnswerUpdated",
                                                                     "inputs": [{"type": "int256", "name": "current",
                                                                                 "indexed": True,
                                                                                 "internalType": "int256"},
                                                                                {"type": "uint256", "name": "roundId",
                                                                                 "indexed": True,
                                                                                 "internalType": "uint256"},
                                                                                {"type": "uint256", "name": "updatedAt",
                                                                                 "indexed": False,
                                                                                 "internalType": "uint256"}],
                                                                     "outputs": [], "anonymous": False},
                  {"type": "event", "name": "NewRound",
                   "inputs": [{"type": "uint256", "name": "roundId", "indexed": True, "internalType": "uint256"},
                              {"type": "address", "name": "startedBy", "indexed": True, "internalType": "address"},
                              {"type": "uint256", "name": "startedAt", "indexed": False, "internalType": "uint256"}],
                   "outputs": [], "anonymous": False}, {"type": "event", "name": "OwnershipTransferRequested",
                                                        "inputs": [{"type": "address", "name": "from", "indexed": True,
                                                                    "internalType": "address"},
                                                                   {"type": "address", "name": "to", "indexed": True,
                                                                    "internalType": "address"}], "outputs": [],
                                                        "anonymous": False},
                  {"type": "event", "name": "OwnershipTransferred",
                   "inputs": [{"type": "address", "name": "from", "indexed": True, "internalType": "address"},
                              {"type": "address", "name": "to", "indexed": True, "internalType": "address"}],
                   "outputs": [], "anonymous": False},
                  {"type": "function", "name": "acceptOwnership", "inputs": [], "outputs": [],
                   "stateMutability": "nonpayable"}, {"type": "function", "name": "accessController", "inputs": [],
                                                      "outputs": [{"type": "address", "name": "",
                                                                   "internalType": "contract AccessControllerInterface"}],
                                                      "stateMutability": "view"},
                  {"type": "function", "name": "aggregator", "inputs": [],
                   "outputs": [{"type": "address", "name": "", "internalType": "address"}], "stateMutability": "view"},
                  {"type": "function", "name": "confirmAggregator",
                   "inputs": [{"type": "address", "name": "_aggregator", "internalType": "address"}], "outputs": [],
                   "stateMutability": "nonpayable"}, {"type": "function", "name": "decimals", "inputs": [], "outputs": [
        {"type": "uint8", "name": "", "internalType": "uint8"}], "stateMutability": "view"},
                  {"type": "function", "name": "description", "inputs": [],
                   "outputs": [{"type": "string", "name": "", "internalType": "string"}], "stateMutability": "view"},
                  {"type": "function", "name": "getAnswer",
                   "inputs": [{"type": "uint256", "name": "_roundId", "internalType": "uint256"}],
                   "outputs": [{"type": "int256", "name": "", "internalType": "int256"}], "stateMutability": "view"},
                  {"type": "function", "name": "getRoundData",
                   "inputs": [{"type": "uint80", "name": "_roundId", "internalType": "uint80"}],
                   "outputs": [{"type": "uint80", "name": "roundId", "internalType": "uint80"},
                               {"type": "int256", "name": "answer", "internalType": "int256"},
                               {"type": "uint256", "name": "startedAt", "internalType": "uint256"},
                               {"type": "uint256", "name": "updatedAt", "internalType": "uint256"},
                               {"type": "uint80", "name": "answeredInRound", "internalType": "uint80"}],
                   "stateMutability": "view"}, {"type": "function", "name": "getTimestamp", "inputs": [
        {"type": "uint256", "name": "_roundId", "internalType": "uint256"}],
                                                "outputs": [{"type": "uint256", "name": "", "internalType": "uint256"}],
                                                "stateMutability": "view"},
                  {"type": "function", "name": "latestAnswer", "inputs": [],
                   "outputs": [{"type": "int256", "name": "", "internalType": "int256"}], "stateMutability": "view"},
                  {"type": "function", "name": "latestRound", "inputs": [],
                   "outputs": [{"type": "uint256", "name": "", "internalType": "uint256"}], "stateMutability": "view"},
                  {"type": "function", "name": "latestRoundData", "inputs": [],
                   "outputs": [{"type": "uint80", "name": "roundId", "internalType": "uint80"},
                               {"type": "int256", "name": "answer", "internalType": "int256"},
                               {"type": "uint256", "name": "startedAt", "internalType": "uint256"},
                               {"type": "uint256", "name": "updatedAt", "internalType": "uint256"},
                               {"type": "uint80", "name": "answeredInRound", "internalType": "uint80"}],
                   "stateMutability": "view"}, {"type": "function", "name": "latestTimestamp", "inputs": [],
                                                "outputs": [{"type": "uint256", "name": "", "internalType": "uint256"}],
                                                "stateMutability": "view"},
                  {"type": "function", "name": "owner", "inputs": [],
                   "outputs": [{"type": "address", "name": "", "internalType": "address payable"}],
                   "stateMutability": "view"}, {"type": "function", "name": "phaseAggregators",
                                                "inputs": [{"type": "uint16", "name": "", "internalType": "uint16"}],
                                                "outputs": [{"type": "address", "name": "",
                                                             "internalType": "contract AggregatorV2V3Interface"}],
                                                "stateMutability": "view"},
                  {"type": "function", "name": "phaseId", "inputs": [],
                   "outputs": [{"type": "uint16", "name": "", "internalType": "uint16"}], "stateMutability": "view"},
                  {"type": "function", "name": "proposeAggregator",
                   "inputs": [{"type": "address", "name": "_aggregator", "internalType": "address"}], "outputs": [],
                   "stateMutability": "nonpayable"}, {"type": "function", "name": "proposedAggregator", "inputs": [],
                                                      "outputs": [{"type": "address", "name": "",
                                                                   "internalType": "contract AggregatorV2V3Interface"}],
                                                      "stateMutability": "view"},
                  {"type": "function", "name": "proposedGetRoundData",
                   "inputs": [{"type": "uint80", "name": "_roundId", "internalType": "uint80"}],
                   "outputs": [{"type": "uint80", "name": "roundId", "internalType": "uint80"},
                               {"type": "int256", "name": "answer", "internalType": "int256"},
                               {"type": "uint256", "name": "startedAt", "internalType": "uint256"},
                               {"type": "uint256", "name": "updatedAt", "internalType": "uint256"},
                               {"type": "uint80", "name": "answeredInRound", "internalType": "uint80"}],
                   "stateMutability": "view"}, {"type": "function", "name": "proposedLatestRoundData", "inputs": [],
                                                "outputs": [
                                                    {"type": "uint80", "name": "roundId", "internalType": "uint80"},
                                                    {"type": "int256", "name": "answer", "internalType": "int256"},
                                                    {"type": "uint256", "name": "startedAt", "internalType": "uint256"},
                                                    {"type": "uint256", "name": "updatedAt", "internalType": "uint256"},
                                                    {"type": "uint80", "name": "answeredInRound",
                                                     "internalType": "uint80"}], "stateMutability": "view"},
                  {"type": "function", "name": "setController",
                   "inputs": [{"type": "address", "name": "_accessController", "internalType": "address"}],
                   "outputs": [], "stateMutability": "nonpayable"}, {"type": "function", "name": "transferOwnership",
                                                                     "inputs": [{"type": "address", "name": "_to",
                                                                                 "internalType": "address"}],
                                                                     "outputs": [], "stateMutability": "nonpayable"},
                  {"type": "function", "name": "version", "inputs": [],
                   "outputs": [{"type": "uint256", "name": "", "internalType": "uint256"}], "stateMutability": "view"}]
PRESALE_BLAST_ABI = [
  {
    "inputs": [
      {
        "internalType": "contract AggregatorV3Interface",
        "name": "COIN_PRICE_FEED_",
        "type": "address"
      },
      {
        "internalType": "contract IERC20",
        "name": "usdtToken_",
        "type": "address"
      },
      {
        "internalType": "contract IERC20",
        "name": "usdcToken_",
        "type": "address"
      },
      {
        "internalType": "contract IERC20",
        "name": "usdbToken_",
        "type": "address"
      },
      {
        "internalType": "contract IERC20",
        "name": "wethToken_",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "protocolWallet_",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "admin",
        "type": "address"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "constructor"
  },
  {
    "inputs": [],
    "name": "EnforcedPause",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "ExpectedPause",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "owner",
        "type": "address"
      }
    ],
    "name": "OwnableInvalidOwner",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "OwnableUnauthorizedAccount",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "SafeTransferFailed",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "SafeTransferFromFailed",
    "type": "error"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "previousOwner",
        "type": "address"
      },
      {
        "indexed": True,
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
      }
    ],
    "name": "OwnershipTransferred",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": False,
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "Paused",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "currentStage",
        "type": "uint256"
      }
    ],
    "name": "StageUpdated",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": True,
        "internalType": "address",
        "name": "token",
        "type": "address"
      },
      {
        "indexed": True,
        "internalType": "address",
        "name": "user",
        "type": "address"
      },
      {
        "indexed": True,
        "internalType": "address",
        "name": "referrer",
        "type": "address"
      },
      {
        "indexed": False,
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "TokensBought",
    "type": "event"
  },
  {
    "anonymous": False,
    "inputs": [
      {
        "indexed": False,
        "internalType": "address",
        "name": "account",
        "type": "address"
      }
    ],
    "name": "Unpaused",
    "type": "event"
  },
  {
    "inputs": [],
    "name": "COIN_PRICE_FEED",
    "outputs": [
      {
        "internalType": "contract AggregatorV3Interface",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "PRICEFEED_DECIMALS",
    "outputs": [
      {
        "internalType": "uint8",
        "name": "",
        "type": "uint8"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "STABLETOKEN_PRICE",
    "outputs": [
      {
        "internalType": "int32",
        "name": "",
        "type": "int32"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "TOKEN_PRECISION",
    "outputs": [
      {
        "internalType": "uint8",
        "name": "",
        "type": "uint8"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "user",
        "type": "address"
      }
    ],
    "name": "balances",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "balance",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "referrer",
        "type": "address"
      }
    ],
    "name": "depositCoin",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "internalType": "address",
        "name": "referrer",
        "type": "address"
      }
    ],
    "name": "depositCoinTo",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "referrer",
        "type": "address"
      }
    ],
    "name": "depositUSDB",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "referrer",
        "type": "address"
      }
    ],
    "name": "depositUSDBTo",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "referrer",
        "type": "address"
      }
    ],
    "name": "depositUSDC",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "referrer",
        "type": "address"
      }
    ],
    "name": "depositUSDCTo",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "referrer",
        "type": "address"
      }
    ],
    "name": "depositUSDT",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "referrer",
        "type": "address"
      }
    ],
    "name": "depositUSDTTo",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "referrer",
        "type": "address"
      }
    ],
    "name": "depositWETH",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "to",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      },
      {
        "internalType": "address",
        "name": "referrer",
        "type": "address"
      }
    ],
    "name": "depositWETHTo",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "owner",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "pause",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "paused",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "protocolWallet",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "renounceOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "contract IERC20",
        "name": "token",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "rescueFunds",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "stageIterator_",
        "type": "uint256"
      }
    ],
    "name": "setStage",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "stageIterator",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "name": "stages",
    "outputs": [
      {
        "internalType": "uint96",
        "name": "cost",
        "type": "uint96"
      },
      {
        "internalType": "uint160",
        "name": "amount",
        "type": "uint160"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "totalSoldInUSD",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "totalTokensSold",
    "outputs": [
      {
        "internalType": "uint256",
        "name": "",
        "type": "uint256"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "newOwner",
        "type": "address"
      }
    ],
    "name": "transferOwnership",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "unpause",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "wallet",
        "type": "address"
      }
    ],
    "name": "updateProtocolWallet",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "updateTotalSold",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "usdbToken",
    "outputs": [
      {
        "internalType": "contract IERC20",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "usdcToken",
    "outputs": [
      {
        "internalType": "contract IERC20",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "usdtToken",
    "outputs": [
      {
        "internalType": "contract IERC20",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "wethToken",
    "outputs": [
      {
        "internalType": "contract IERC20",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }
]