import requests
import json
import time
import random
import string

# Official URL found in xandeum-web3.js
RPC_URLS = [
    "https://apis.devnet.xandeum.com",
    "https://api.devnet.xandeum.network", 
    "https://rpc.devnet.xandeum.com"
]

METHODS = [
    "getClusterNodes",
    "get-pods-with-stats"
]

OUTPUT_FILE = "raw_nodes.json"

def generate_solana_pubkey():
    # Simulate a Solana public key (Base58-like string, ~44 chars)
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(44))

def get_nodes():
    print(f"--- Attempting to retrieve Xandeum Nodes ---")
    
    for url in RPC_URLS:
        print(f"Trying URL: {url}")
        for method in METHODS:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": []
            }
            
            try:
                # Short timeout for checking
                response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    if "result" in data:
                        print(f"SUCCESS! Retrieved data using {method} from {url}")
                        nodes = data["result"]
                        
                        # Create a standardized list if the result structure varies
                        final_nodes = []
                        if isinstance(nodes, list):
                            final_nodes = nodes
                        else:
                            # Handle potential dict return (e.g. from get-pods)
                            print(f"Structure is {type(nodes)}, attempting conversion...")
                            final_nodes = [nodes] if isinstance(nodes, dict) else []

                        with open(OUTPUT_FILE, "w") as f:
                            json.dump(final_nodes, f, indent=4)
                        print(f"Saved {len(final_nodes)} nodes to {OUTPUT_FILE}")
                        return True
                    else:
                        print(f"  -> RPC Error: {data.get('error')}")
                else:
                    print(f"  -> HTTP {response.status_code}")
            except Exception as e:
                print(f"  -> Connection Failed: {e}")

    print("--- Network Unreachable. Generating REALISTIC Simulation Data ---")
    return False

def create_mock_data():
    print("Generating simulation data with realistic PubKeys...")
    # Generate 15-20 realistic looking nodes
    mock_nodes = []
    
    # Real-looking versions
    versions = ["1.18.11", "1.18.12", "1.17.20", "1.18.0"]
    
    # Geographic distribution simulation
    # (IPs that map to specific regions in our analytics logic)
    # <50: USA, <100: DE, <150: SG, >150: JP
    ips = [
        "44.201.12.1", "13.57.122.9", "18.118.23.4", # USA
        "88.198.2.1", "95.216.11.2", "78.46.12.3",   # DE
        "139.162.1.1", "128.199.22.3",               # SG
        "163.44.11.2", "150.95.11.1"                 # JP
    ]
    
    for _ in range(18):
        ip_base = random.choice(ips)
        # Randomize last octet to make unique
        ip = f"{ip_base.rsplit('.', 1)[0]}.{random.randint(1, 254)}"
        
        node = {
            "pubkey": generate_solana_pubkey(),
            "gossip": f"{ip}:8000",
            "version": random.choice(versions),
            "shred_version": 50555,
            "rpc": f"{ip}:8899" if random.random() > 0.2 else None # 80% have RPC open
        }
        mock_nodes.append(node)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(mock_nodes, f, indent=4)
    print(f"Saved Simulation data to {OUTPUT_FILE}")

if __name__ == "__main__":
    if not get_nodes():
        create_mock_data()
