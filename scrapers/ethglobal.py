def fetch(limit=20):
    """ETHGlobal events are JS-rendered — return as pointer for 'Also check' section."""
    return [{
        "source": "ETHGlobal",
        "title": "ETHGlobal Hackathons & Events",
        "url": "https://ethglobal.com/events",
        "prize": "Various",
        "deadline": "See website",
        "track": "web3",
        "_is_pointer": True,
        "raw": "ETHGlobal runs the largest Ethereum hackathons worldwide, with prize pools funded by major Web3 sponsors.",
    }]
