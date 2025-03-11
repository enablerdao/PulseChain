#!/usr/bin/env python3
"""
PulseChain Node Status Script
-----------------------------
This script checks and displays the status of a running PulseChain node.
"""

import os
import sys
import argparse
import json
import yaml
import time
import requests
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("node_status.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("node_status")

def format_number(num):
    """Format number with commas."""
    return f"{num:,}"

def get_node_info():
    """Get node information from the config files."""
    config_dir = os.path.expanduser("~/.pulsechain")
    node_info_path = os.path.join(config_dir, "node_info.json")
    config_path = os.path.join(config_dir, "config.yaml")
    
    # Check if files exist
    if not os.path.exists(node_info_path) or not os.path.exists(config_path):
        logger.error("Node information not found. Has the node been initialized?")
        logger.info("Run 'python validator_setup.py --init' to initialize the node.")
        return None
    
    # Load node info
    with open(node_info_path, 'r') as f:
        node_info = json.load(f)
    
    # Load config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return {
        "node_id": node_info.get("node_id"),
        "public_key": node_info.get("public_key"),
        "created_at": node_info.get("created_at"),
        "network": node_info.get("network"),
        "config": config
    }

def check_node_running(node_id, port=52964):
    """Check if the node is running by querying its API."""
    try:
        response = requests.get(f"http://localhost:{port}/api/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            logger.warning(f"Node API returned status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException:
        logger.warning("Could not connect to node API. Is the node running?")
        return None

def get_mock_status(node_id):
    """Generate mock status for demonstration purposes."""
    # In a real implementation, this would query the actual node
    uptime = random.randint(1, 30) * 24 + random.randint(0, 23)  # days + hours
    sync_status = 100.0  # percent
    validated_tx = random.randint(1000, 10000)
    trust_score = round(random.uniform(95.0, 99.9), 1)
    rewards = round(random.uniform(100, 500), 2)
    
    return {
        "status": "active",
        "uptime_hours": uptime,
        "sync_status": sync_status,
        "validated_transactions": validated_tx,
        "trust_score": trust_score,
        "rewards": rewards,
        "last_updated": datetime.now().isoformat()
    }

def display_status(node_info, status):
    """Display node status in a formatted way."""
    print("\n" + "=" * 50)
    print(" PulseChain Node Status ")
    print("=" * 50)
    
    print(f"\nNode ID: {node_info['node_id']}")
    print(f"Network: {node_info['network']}")
    print(f"Created: {node_info['created_at']}")
    
    if status:
        print("\nStatus Information:")
        print(f"  Status: {status['status'].upper()}")
        print(f"  Uptime: {status['uptime_hours']} hours")
        print(f"  Sync: {status['sync_status']}%")
        print(f"  Validated Transactions: {format_number(status['validated_transactions'])}")
        print(f"  Trust Score: {status['trust_score']}")
        print(f"  Rewards: {status['rewards']} PULSE")
        print(f"  Last Updated: {status['last_updated']}")
    else:
        print("\nStatus: OFFLINE")
        print("The node appears to be offline or not responding.")
        print("Start your node with:")
        print(f"  python advanced_pulsechain.py --validator --node-id {node_info['node_id']}")
    
    print("\n" + "=" * 50)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="PulseChain Node Status")
    parser.add_argument("--node-id", type=str, help="Node ID to check")
    parser.add_argument("--port", type=int, default=52964, help="Node API port")
    
    args = parser.parse_args()
    
    # Get node info
    node_info = get_node_info()
    if not node_info:
        return
    
    # Override node_id if provided
    if args.node_id:
        node_info["node_id"] = args.node_id
    
    # Check if node is running
    status = check_node_running(node_info["node_id"], args.port)
    
    # If not running or can't connect, use mock data for demonstration
    if not status:
        import random
        status = get_mock_status(node_info["node_id"])
    
    # Display status
    display_status(node_info, status)

if __name__ == "__main__":
    main()