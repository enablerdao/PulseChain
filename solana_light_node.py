#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PulseChain - Solana Light Node
============================

This script runs a lightweight node that fetches data from the Solana blockchain
and integrates it into the PulseChain consensus mechanism as environmental data.
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
from pulsechain.consensus.env_sync import EnvDataIntegrator, EnvDataSourceType
from pulsechain.core.region_manager import RegionManager
from pulsechain.network.heartbeat import HeartbeatProtocol
from pulsechain.network.region_sync import RegionSync
from pulsechain.utils.solana_data_source import SolanaDataSource

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("solana_light_node.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("solana_light_node")


class SolanaLightNode:
    """
    Solana Light Node for PulseChain.
    
    This class runs a lightweight node that fetches data from the Solana blockchain
    and integrates it into the PulseChain consensus mechanism as environmental data.
    """
    
    def __init__(self, 
                 node_id: str,
                 region: str,
                 port: int = 52966,
                 solana_cluster: str = "mainnet-beta",
                 solana_update_interval: float = 5.0,
                 leader_address: Optional[str] = None,
                 heartbeat_interval: float = 0.1):
        """
        Initialize the Solana light node.
        
        Args:
            node_id: Identifier for this node
            region: Geographic region for this node
            port: Network port to listen on
            solana_cluster: Solana cluster to connect to
            solana_update_interval: How often to update Solana data (in seconds)
            leader_address: Address of the PoH leader node to connect to
            heartbeat_interval: Interval between heartbeats in seconds
        """
        self.node_id = node_id
        self.region = region
        self.port = port
        self.leader_address = leader_address
        
        # Initialize components
        logger.info("Initializing PoH generator...")
        self.poh_generator = PoHGenerator(target_hash_rate=10000)  # Lower hash rate for light nodes
        
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
        
        logger.info("Initializing Solana data source...")
        self.solana_source = SolanaDataSource(
            primary_cluster=solana_cluster,
            update_interval=solana_update_interval
        )
        
        logger.info("Initializing environmental data integrator...")
        self.env_integrator = EnvDataIntegrator(
            poh_consensus=self.poh_consensus
        )
        
        # Connect components
        self._connect_components()
        
        # Signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"Solana Light Node initialized: {node_id} in region {region}")
    
    def _connect_components(self) -> None:
        """Connect the various components together."""
        # Connect Solana data source to environmental data integrator
        self.solana_source.on_data_updated(self._on_solana_data_updated)
        
        # Connect heartbeat protocol to consensus
        self.heartbeat.on_heartbeat(self._on_heartbeat)
        
        # Connect PoH consensus callbacks
        self.poh_consensus.on_new_slot(self._on_new_slot)
        self.poh_consensus.on_slot_finalized(self._on_slot_finalized)
        
        # Connect region manager to consensus
        self.region_manager.on_coordinator_change(self._on_coordinator_change)
    
    def _on_solana_data_updated(self, data: Dict[str, Any]) -> None:
        """
        Callback for when Solana data is updated.
        
        Args:
            data: The updated Solana data
        """
        logger.debug(f"Received new Solana data: slot={data.get('slot')}")
        
        # Add Solana data as environmental data source
        self.env_integrator.add_source(
            source_id="solana",
            source_type=EnvDataSourceType.CUSTOM,
            api_url=None,  # Not using an API, data is provided directly
            update_interval=self.solana_source.update_interval,
            weight=1.0  # High weight for Solana data
        )
        
        # Create environmental data from Solana data
        env_data = {
            "timestamp": data.get("timestamp", time.time()),
            "solana_slot": data.get("slot"),
            "solana_block_time": data.get("block_time"),
            "solana_health": data.get("health"),
            "solana_cluster": data.get("cluster")
        }
        
        # Add performance data if available
        if "performance" in data and data["performance"]:
            # Extract the most recent performance sample
            recent_sample = data["performance"][0] if data["performance"] else None
            if recent_sample:
                env_data["solana_num_transactions"] = recent_sample.get("numTransactions")
                env_data["solana_num_slots"] = recent_sample.get("numSlots")
                env_data["solana_sample_period_secs"] = recent_sample.get("samplePeriodSecs")
        
        # Add version data if available
        if "version" in data and data["version"]:
            env_data["solana_version"] = data["version"].get("solana-core")
        
        # Update the PoH generator with the Solana data
        self.poh_generator.next(env_data)
        
        # If we're the leader, integrate the data
        if self.poh_consensus.is_leader:
            logger.debug("Integrating Solana data as leader")
            # In a real implementation, this would properly integrate with the env_integrator
    
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
        """Start the Solana light node."""
        logger.info("Starting Solana light node...")
        
        # Connect to leader if specified
        if self.leader_address:
            self.connect_to_leader()
        
        # Start components
        self.poh_generator.start()
        self.poh_consensus.start()
        self.region_manager.start()
        self.heartbeat.start()
        self.region_sync.start()
        self.solana_source.start()
        
        # Register as a validator
        self.poh_consensus.register_validator(self.node_id)
        
        logger.info("Solana light node started")
    
    def stop(self) -> None:
        """Stop the Solana light node."""
        logger.info("Stopping Solana light node...")
        
        # Stop components in reverse order
        self.solana_source.stop()
        self.region_sync.stop()
        self.heartbeat.stop()
        self.region_manager.stop()
        self.poh_consensus.stop()
        self.poh_generator.stop()
        
        logger.info("Solana light node stopped")
    
    def run(self) -> None:
        """Run the Solana light node."""
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
        
        solana_status = self.solana_source.get_status()
        solana_latest = self.solana_source.get_latest_data()
        
        logger.info(f"Status: PoH={poh_status}, Region={region_status}, Heartbeat={heartbeat_status}")
        logger.info(f"Solana: cluster={solana_status['primary_cluster']}, slot={solana_latest.get('slot')}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="PulseChain Solana Light Node")
    
    parser.add_argument('--node-id', type=str, default=f"solana_node_{int(time.time())}",
                       help="Unique identifier for this node")
    
    parser.add_argument('--region', type=str, default="default",
                       help="Geographic region for this node")
    
    parser.add_argument('--port', type=int, default=52966,
                       help="Network port to listen on")
    
    parser.add_argument('--solana-cluster', type=str, default="mainnet-beta",
                       choices=["mainnet-beta", "testnet", "devnet", "localnet"],
                       help="Solana cluster to connect to")
    
    parser.add_argument('--solana-update-interval', type=float, default=5.0,
                       help="How often to update Solana data (in seconds)")
    
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
    
    # Create and run the Solana light node
    node = SolanaLightNode(
        node_id=args.node_id,
        region=args.region,
        port=args.port,
        solana_cluster=args.solana_cluster,
        solana_update_interval=args.solana_update_interval,
        leader_address=args.leader_address or None,
        heartbeat_interval=args.heartbeat_interval
    )
    
    node.run()


if __name__ == "__main__":
    main()