import json
import pandas as pd
import geoip2.database
import datetime
import random # For mock geo-location if DB not found

INPUT_FILE = "raw_nodes.json"

def load_data():
    try:
        with open(INPUT_FILE, "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found.")
        return []

def enrich_data(nodes):
    print("--- Enriching Node Data ---")
    enriched_list = []
    
    # In a real scenario, we'd use the MaxMind City database.
    # For this hackathon/mock setup, we will simulate Geo lookup if DB is missing.
    try:
        reader = geoip2.database.Reader('GeoLite2-City.mmdb')
        has_db = True
    except FileNotFoundError:
        print("Warning: GeoLite2-City.mmdb not found. Using Mock Geo Logic.")
        has_db = False

    for node in nodes:
        # Extract IP from gossip address (e.g., "145.2.33.1:8000")
        gossip_addr = node.get("gossip")
        ip = gossip_addr.split(":")[0] if gossip_addr else None
        
        country = "Unknown"
        city = "Unknown"
        lat = 0.0
        lon = 0.0
        
        if ip:
            if has_db:
                try:
                    response = reader.city(ip)
                    country = response.country.name
                    city = response.city.name
                    lat = response.location.latitude
                    lon = response.location.longitude
                except Exception:
                    pass
            else:
                # Mock Geo Logic based on IP first byte
                first_byte = int(ip.split('.')[0])
                if first_byte < 50:
                    country = "USA"
                    city = "New York"
                    lat, lon = 40.7128, -74.0060
                elif first_byte < 100:
                    country = "Germany"
                    city = "Frankfurt"
                    lat, lon = 50.1109, 8.6821
                elif first_byte < 150:
                    country = "Singapore"
                    city = "Singapore"
                    lat, lon = 1.3521, 103.8198
                else:
                    country = "Japan"
                    city = "Tokyo"
                    lat, lon = 35.6762, 139.6503
        
        # Version Parsing
        version = node.get("version", "0.0.0")
        
        # Simulated Uptime (since raw gossip doesn't always have it)
        # In real data, 'shred_version' matching the cluster is a proxy for health
        is_healthy = True if node.get("rpc") else False # Mock logic: if RPC open, it's healthy
        
        entry = {
            "pubkey": node.get("pubkey"),
            "ip": ip,
            "version": version,
            "country": country,
            "city": city,
            "lat": lat,
            "lon": lon,
            "status": "Active" if is_healthy else "Offline",
            "last_seen": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        enriched_list.append(entry)

    df = pd.DataFrame(enriched_list)
    print(f"Processed {len(df)} nodes.")
    return df

def analyze_network(df):
    print("\n--- Network Analytics ---")
    
    # KPI 1: Total Nodes
    total_nodes = len(df)
    
    # KPI 2: Active vs Offline
    status_counts = df['status'].value_counts()
    
    # KPI 3: Version Distribution
    version_counts = df['version'].value_counts()
    
    # KPI 4: Text Summary
    top_country = df['country'].mode()[0] if not df.empty else "None"
    
    stats = {
        "total_nodes": int(total_nodes),
        "active_nodes": int(status_counts.get("Active", 0)),
        "offline_nodes": int(status_counts.get("Offline", 0)),
        "top_country": str(top_country)
    }
    
    print(json.dumps(stats, indent=4))
    return stats

if __name__ == "__main__":
    raw_data = load_data()
    if raw_data:
        df = enrich_data(raw_data)
        analyze_network(df)
        
        # Save processed data for Dashboard (Phase 3)
        df.to_csv("processed_nodes.csv", index=False)
        print("Enriched data saved to processed_nodes.csv")
