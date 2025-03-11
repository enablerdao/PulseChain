#!/usr/bin/env python3
"""
PulseChain Validator Setup Script
---------------------------------
This script helps users set up a PulseChain validator node.
It handles the initial configuration, key generation, and registration.
"""

import os
import sys
import argparse
import json
import random
import string
import time
import yaml
import hashlib
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("validator_setup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("validator_setup")

# Default configuration
DEFAULT_CONFIG = {
    "node": {
        "name": "PulseChainNode",
        "network": "mainnet",
        "port": 52964
    },
    "validator": {
        "enabled": True,
        "stake_amount": 1000
    },
    "environmental_data": {
        "sources": {
            "weather_api": True,
            "bitcoin_data": True,
            "browser_data": True
        }
    },
    "zero_energy": {
        "enabled": True,
        "target_cpu_usage": 30.0
    }
}

def generate_node_id():
    """Generate a unique node ID."""
    # Create a random string
    random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    # Add timestamp for uniqueness
    timestamp = int(time.time())
    # Create a hash
    node_id = hashlib.sha256(f"{random_str}{timestamp}".encode()).hexdigest()[:16]
    return node_id

def create_config_file(config_path, node_id):
    """Create the configuration file."""
    config = DEFAULT_CONFIG.copy()
    config["node"]["id"] = node_id
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # Write config to file
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    logger.info(f"Configuration file created at: {config_path}")
    return config

def create_validator_keys(keys_dir, node_id):
    """Create validator keys."""
    # Ensure directory exists
    os.makedirs(keys_dir, exist_ok=True)
    
    # Generate mock keys (in a real implementation, this would use proper cryptography)
    private_key = hashlib.sha256(f"private_{node_id}".encode()).hexdigest()
    public_key = hashlib.sha256(f"public_{node_id}".encode()).hexdigest()
    
    # Save keys to files
    with open(os.path.join(keys_dir, "validator_private.key"), 'w') as f:
        f.write(private_key)
    
    with open(os.path.join(keys_dir, "validator_public.key"), 'w') as f:
        f.write(public_key)
    
    logger.info(f"Validator keys created in: {keys_dir}")
    return private_key, public_key

def initialize_validator(args):
    """Initialize the validator node."""
    logger.info("Initializing PulseChain validator node...")
    
    # Generate node ID
    node_id = generate_node_id()
    logger.info(f"Generated Node ID: {node_id}")
    
    # Create config directory
    config_dir = os.path.expanduser("~/.pulsechain")
    config_path = os.path.join(config_dir, "config.yaml")
    keys_dir = os.path.join(config_dir, "keys")
    
    # Create config file
    config = create_config_file(config_path, node_id)
    
    # Create validator keys
    private_key, public_key = create_validator_keys(keys_dir, node_id)
    
    # Create node info file
    node_info = {
        "node_id": node_id,
        "public_key": public_key,
        "created_at": datetime.now().isoformat(),
        "network": config["node"]["network"]
    }
    
    with open(os.path.join(config_dir, "node_info.json"), 'w') as f:
        json.dump(node_info, f, indent=2)
    
    logger.info("Validator node initialization complete!")
    logger.info(f"Node ID: {node_id}")
    logger.info(f"Configuration directory: {config_dir}")
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Review and edit the configuration file if needed:")
    logger.info(f"   nano {config_path}")
    logger.info("2. Start your validator node:")
    logger.info(f"   python advanced_pulsechain.py --validator --node-id {node_id}")
    logger.info("3. Register your validator at:")
    logger.info("   https://pulsechain.example.com/validators/register")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="PulseChain Validator Setup")
    parser.add_argument("--init", action="store_true", help="Initialize validator node")
    parser.add_argument("--config", type=str, default="~/.pulsechain/config.yaml", 
                        help="Path to config file")
    
    args = parser.parse_args()
    
    if args.init:
        initialize_validator(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()