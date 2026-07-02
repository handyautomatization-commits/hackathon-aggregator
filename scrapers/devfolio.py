def fetch(limit=20):
    """Devfolio hosts Web3 + general hackathons. Its search API exposes no prize
    amounts (items would be dropped by the prize filter), so return a pointer for
    the 'Also check' section instead of individual listings."""
    return [{
        "source": "Devfolio",
        "title": "Devfolio Open Hackathons",
        "url": "https://devfolio.co/hackathons",
        "prize": "Various",
        "deadline": "See website",
        "track": "web3",
        "_is_pointer": True,
        "raw": "Devfolio hosts Web3 and general hackathons (India + global), many with token, DeFi and on-chain tracks.",
    }]
