#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PulseChain - Validator Node
==========================

This script runs a PulseChain node as a validator.
It validates the PoH timeline and participates in consensus.
"""

import os
import sys
import time
import json
import argparse
import logging
import signal
from typing import Dict, List, Optional, Any

from pulsechain.core.poh_generator import PoHGenerator
from pulsechain.consensus.poh import PoHConsensus
from pulsechain.core.region_manager import RegionManager
from pulsechain.network.heartbeat import HeartbeatProtocol
from pulsechain.network.region_sync import RegionSync

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("validator_node.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("validator_node")


class ValidatorNode:
    """
    Validator Node for PulseChain.
    
    This class runs a PulseChain node as a validator, validating the PoH timeline
    and participating in consensus.
    """
    
    def __init__(self, 
                 node_id: str,
                 region: str,
                 port: int = 52965,
                 leader_address: Optional[str] = None,
                 heartbeat_interval: float = 0.1):
        """
        Initialize the validator node.
        
        Args:
            node_id: Identifier for this node
            region: Geographic region for this node
            port: Network port to listen on
            leader_address: Address of the PoH leader node to connect to
            heartbeat_interval: Interval between heartbeats in seconds
        """
        self.node_id = node_id
        self.region = region
        self.port = port
        self.leader_address = leader_address
        
        # Initialize components
        logger.info("Initializing PoH generator...")
        self.poh_generator = PoHGenerator(target_hash_rate=10000)  # Lower hash rate for validators
        
        logger.info("Initializing PoH consensus...")
        self.poh_consensus = PoHConsensus(
            node_id=node_id,
            region=region,
            poh_generator=self.poh_generator
        )
        
        logger.info("Initializing region manager...")
        self.region_manager = RegionManager(
            node_id=node_id,
            primary_region=region
        )
        
        logger.info("Initializing heartbeat protocol...")
        self.heartbeat = HeartbeatProtocol(
            node_id=node_id,
            region=region,
            poh_consensus=self.poh_consensus,
            heartbeat_interval=heartbeat_interval
        )
        
        logger.info("Initializing region sync...")
        self.region_sync = RegionSync(
            region_manager=self.region_manager,
            poh_consensus=self.poh_consensus,
            sync_interval=1.0  # 1 second
        )
        
        # Connect components
        self._connect_components()
        
        # Signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"Validator Node initialized: {node_id} in region {region}")
    
    def _connect_components(self) -> None:
        """Connect the various components together."""
        # Connect heartbeat protocol to consensus
        self.heartbeat.on_heartbeat(self._on_heartbeat)
        
        # Connect PoH consensus callbacks
        self.poh_consensus.on_new_slot(self._on_new_slot)
        self.poh_consensus.on_slot_finalized(self._on_slot_finalized)
        
        # Connect region manager to consensus
        self.region_manager.on_coordinator_change(self._on_coordinator_change)
    
    def _on_heartbeat(self, heartbeat: Any) -> None:
        """
        Callback for when a heartbeat is received.
        
        Args:
            heartbeat: The received heartbeat
        """
        # Process the heartbeat
        logger.debug(f"Received heartbeat from {heartbeat.node_id}")
        
        # Confirm the slot if it's from a leader
        if heartbeat.node_id == self.poh_consensus.current_leader_id:
            self.poh_consensus.confirm_slot(heartbeat.poh_slot, self.node_id)
    
    def _on_new_slot(self, slot: Any) -> None:
        """
        Callback for when a new PoH slot is created.
        
        Args:
            slot: The new slot
        """
        logger.debug(f"New slot created: {slot.slot_number}, leader: {slot.leader_id}")
        
        # If we're not the leader, confirm the slot
        if slot.leader_id != self.node_id:
            self.poh_consensus.confirm_slot(slot.slot_number, self.node_id)
    
    def _on_slot_finalized(self, slot: Any) -> None:
        """
        Callback for when a PoH slot is finalized.
        
        Args:
            slot: The finalized slot
        """
        logger.debug(f"Slot finalized: {slot.slot_number}, confirmations: {len(slot.confirmations)}")
    
    def _on_coordinator_change(self, region_id: str, coordinator_id: Optional[str]) -> None:
        """
        Callback for when a region's coordinator changes.
        
        Args:
            region_id: The region ID
            coordinator_id: The new coordinator ID, or None if there is no coordinator
        """
        logger.info(f"Region {region_id} coordinator changed to {coordinator_id}")
    
    def _signal_handler(self, sig, frame) -> None:
        """
        Handle signals (e.g., SIGINT, SIGTERM).
        
        Args:
            sig: The signal number
            frame: The current stack frame
        """
        logger.info(f"Received signal {sig}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def connect_to_leader(self) -> bool:
        """
        Connect to the PoH leader node.
        
        Returns:
            True if connected successfully, False otherwise
        """
        if not self.leader_address:
            logger.warning("No leader address specified")
            return False
        
        try:
            # Parse leader address
            host, port = self.leader_address.split(':')
            port = int(port)
            
            logger.info(f"Connecting to leader at {host}:{port}...")
            
            # In a real implementation, this would establish a network connection
            # For now, we just simulate a successful connection
            
            # Register the leader node
            leader_id = f"leader_{host}_{port}"
            self.heartbeat.register_node(
                leader_id,
                b"simulated_public_key",
                self.region
            )
            
            # Register the leader with the PoH consensus
            self.poh_consensus.register_leader(
                leader_id,
                b"simulated_public_key",
                self.region,
                1000.0  # Stake amount
            )
            
            logger.info(f"Connected to leader {leader_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to leader: {e}")
            return False
    
    def start(self) -> None:
        """Start the validator node."""
        logger.info("Starting validator node...")
        
        # Connect to leader if specified
        if self.leader_address:
            self.connect_to_leader()
        
        # Start components
        self.poh_generator.start()
        self.poh_consensus.start()
        self.region_manager.start()
        self.heartbeat.start()
        self.region_sync.start()
        
        # Register as a validator
        self.poh_consensus.register_validator(self.node_id)
        
        logger.info("Validator node started")
    
    def stop(self) -> None:
        """Stop the validator node."""
        logger.info("Stopping validator node...")
        
        # Stop components in reverse order
        self.region_sync.stop()
        self.heartbeat.stop()
        self.region_manager.stop()
        self.poh_consensus.stop()
        self.poh_generator.stop()
        
        logger.info("Validator node stopped")
    
    def run(self) -> None:
        """Run the validator node."""
        self.start()
        
        try:
            # Main loop
            while True:
                # Print status every 10 seconds
                time.sleep(10)
                self._print_status()
                
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.stop()
    
    def _print_status(self) -> None:
        """Print the current status of the node."""
        poh_status = {
            "current_slot": self.poh_consensus.current_slot_number,
            "is_leader": self.poh_consensus.is_leader,
            "current_leader": self.poh_consensus.current_leader_id,
            "finalized_slots": len(self.poh_consensus.finalized_slots)
        }
        
        region_status = {
            "primary_region": self.region_manager.primary_region,
            "is_coordinator": self.region_manager.is_coordinator(self.node_id),
            "connected_regions": len(self.region_manager.get_connected_regions(self.region_manager.primary_region))
        }
        
        heartbeat_status = {
            "active_nodes": len(self.heartbeat.get_active_nodes())
        }
        
        logger.info(f"Status: PoH={poh_status}, Region={region_status}, Heartbeat={heartbeat_status}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="PulseChain Validator Node")
    
    parser.add_argument('--node-id', type=str, default=f"validator_{int(time.time())}",
                       help="Unique identifier for this node")
    
    parser.add_argument('--region', type=str, default="default",
                       help="Geographic region for this node")
    
    parser.add_argument('--port', type=int, default=52965,
                       help="Network port to listen on")
    
    parser.add_argument('--leader-address', type=str, default="",
                       help="Address of the PoH leader node to connect to (host:port)")
    
    parser.add_argument('--heartbeat-interval', type=float, default=0.1,
                       help="Interval between heartbeats in seconds")
    
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       help="Logging level")
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Create and run the validator node
    node = ValidatorNode(
        node_id=args.node_id,
        region=args.region,
        port=args.port,
        leader_address=args.leader_address or None,
        heartbeat_interval=args.heartbeat_interval
    )
    
    node.run()


if __name__ == "__main__":
    main()