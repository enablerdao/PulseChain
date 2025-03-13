#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PulseChain - PoH Leader Node
===========================

This script runs a PulseChain node as a PoH leader.
It generates the PoH timeline and integrates environmental data.
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
from pulsechain.consensus.env_sync import EnvDataIntegrator
from pulsechain.core.region_manager import RegionManager
from pulsechain.network.heartbeat import HeartbeatProtocol
from pulsechain.network.region_sync import RegionSync
from pulsechain.utils.env_data_collector import EnvDataCollector, DataSourceType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("poh_leader.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("poh_leader")


class PoHLeaderNode:
    """
    PoH Leader Node for PulseChain.
    
    This class runs a PulseChain node as a PoH leader, generating the PoH timeline
    and integrating environmental data.
    """
    
    def __init__(self, 
                 node_id: str,
                 region: str,
                 port: int = 52964,
                 env_data_sources: Optional[List[str]] = None,
                 env_config_file: Optional[str] = None,
                 target_hash_rate: int = 100000,
                 slot_duration: float = 0.4):
        """
        Initialize the PoH leader node.
        
        Args:
            node_id: Identifier for this node
            region: Geographic region for this node
            port: Network port to listen on
            env_data_sources: List of environmental data sources to use
            env_config_file: Path to environmental data configuration file
            target_hash_rate: Target hash rate for the PoH generator
            slot_duration: Duration of each PoH slot in seconds
        """
        self.node_id = node_id
        self.region = region
        self.port = port
        
        # Initialize components
        logger.info("Initializing PoH generator...")
        self.poh_generator = PoHGenerator(target_hash_rate=target_hash_rate)
        
        logger.info("Initializing PoH consensus...")
        self.poh_consensus = PoHConsensus(
            node_id=node_id,
            region=region,
            poh_generator=self.poh_generator,
            slot_duration=slot_duration
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
            heartbeat_interval=0.1  # 100ms
        )
        
        logger.info("Initializing region sync...")
        self.region_sync = RegionSync(
            region_manager=self.region_manager,
            poh_consensus=self.poh_consensus,
            sync_interval=1.0  # 1 second
        )
        
        logger.info("Initializing environmental data collector...")
        self.env_collector = EnvDataCollector(config_file=env_config_file)
        
        # Add default data sources if none specified
        if not env_data_sources and not env_config_file:
            env_data_sources = ["time", "system"]
        
        # Add specified data sources
        if env_data_sources:
            for source in env_data_sources:
                self._add_data_source(source)
        
        logger.info("Initializing environmental data integrator...")
        self.env_integrator = EnvDataIntegrator(
            poh_consensus=self.poh_consensus
        )
        
        # Connect components
        self._connect_components()
        
        # Signal handling
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"PoH Leader Node initialized: {node_id} in region {region}")
    
    def _add_data_source(self, source: str) -> None:
        """
        Add a data source to the environmental data collector.
        
        Args:
            source: The source to add (e.g., "time", "market", "weather")
        """
        try:
            if source == "time":
                self.env_collector.add_source(
                    source_id="time",
                    source_type=DataSourceType.TIME,
                    update_interval=10.0
                )
                logger.info("Added time data source")
                
            elif source == "market":
                self.env_collector.add_source(
                    source_id="market",
                    source_type=DataSourceType.MARKET,
                    api_url="https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd",
                    update_interval=30.0
                )
                logger.info("Added market data source")
                
            elif source == "weather":
                self.env_collector.add_source(
                    source_id="weather",
                    source_type=DataSourceType.WEATHER,
                    api_url="https://api.openweathermap.org/data/2.5/weather",
                    params={"q": "London", "appid": "your_api_key"},
                    update_interval=60.0
                )
                logger.info("Added weather data source")
                
            elif source == "network":
                self.env_collector.add_source(
                    source_id="network",
                    source_type=DataSourceType.NETWORK,
                    update_interval=15.0
                )
                logger.info("Added network data source")
                
            elif source == "system":
                self.env_collector.add_source(
                    source_id="system",
                    source_type=DataSourceType.SYSTEM,
                    update_interval=5.0
                )
                logger.info("Added system data source")
                
            else:
                logger.warning(f"Unknown data source: {source}")
                
        except Exception as e:
            logger.error(f"Error adding data source {source}: {e}")
    
    def _connect_components(self) -> None:
        """Connect the various components together."""
        # Connect environmental data collector to integrator
        self.env_collector.on_data_collected(self._on_env_data_collected)
        
        # Connect heartbeat protocol to consensus
        self.heartbeat.on_heartbeat(self._on_heartbeat)
        
        # Connect region manager to consensus
        self.region_manager.on_coordinator_change(self._on_coordinator_change)
    
    def _on_env_data_collected(self, data_point: Any) -> None:
        """
        Callback for when environmental data is collected.
        
        Args:
            data_point: The collected data point
        """
        # Forward to the environmental data integrator
        # In a real implementation, this would properly convert between types
        logger.debug(f"Collected environmental data from {data_point.source_id}")
    
    def _on_heartbeat(self, heartbeat: Any) -> None:
        """
        Callback for when a heartbeat is received.
        
        Args:
            heartbeat: The received heartbeat
        """
        # Process the heartbeat
        logger.debug(f"Received heartbeat from {heartbeat.node_id}")
    
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
    
    def start(self) -> None:
        """Start the PoH leader node."""
        logger.info("Starting PoH leader node...")
        
        # Start components
        self.poh_generator.start()
        self.poh_consensus.start()
        self.region_manager.start()
        self.heartbeat.start()
        self.region_sync.start()
        self.env_collector.start()
        
        logger.info("PoH leader node started")
    
    def stop(self) -> None:
        """Stop the PoH leader node."""
        logger.info("Stopping PoH leader node...")
        
        # Stop components in reverse order
        self.env_collector.stop()
        self.region_sync.stop()
        self.heartbeat.stop()
        self.region_manager.stop()
        self.poh_consensus.stop()
        self.poh_generator.stop()
        
        logger.info("PoH leader node stopped")
    
    def run(self) -> None:
        """Run the PoH leader node."""
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
            "hash_rate": self.poh_generator.get_hash_rate()
        }
        
        region_status = {
            "primary_region": self.region_manager.primary_region,
            "is_coordinator": self.region_manager.is_coordinator(self.node_id),
            "connected_regions": len(self.region_manager.get_connected_regions(self.region_manager.primary_region))
        }
        
        heartbeat_status = {
            "active_nodes": len(self.heartbeat.get_active_nodes())
        }
        
        env_status = {
            "sources": len(self.env_collector.sources),
            "data_points": sum(len(points) for points in self.env_collector.data_points.values())
        }
        
        logger.info(f"Status: PoH={poh_status}, Region={region_status}, Heartbeat={heartbeat_status}, Env={env_status}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="PulseChain PoH Leader Node")
    
    parser.add_argument('--node-id', type=str, default=f"node_{int(time.time())}",
                       help="Unique identifier for this node")
    
    parser.add_argument('--region', type=str, default="default",
                       help="Geographic region for this node")
    
    parser.add_argument('--port', type=int, default=52964,
                       help="Network port to listen on")
    
    parser.add_argument('--env-data-sources', type=str, default="",
                       help="Comma-separated list of environmental data sources to use")
    
    parser.add_argument('--env-config', type=str, default="",
                       help="Path to environmental data configuration file")
    
    parser.add_argument('--target-hash-rate', type=int, default=100000,
                       help="Target hash rate for the PoH generator")
    
    parser.add_argument('--slot-duration', type=float, default=0.4,
                       help="Duration of each PoH slot in seconds")
    
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                       help="Logging level")
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Parse environmental data sources
    env_data_sources = args.env_data_sources.split(',') if args.env_data_sources else None
    
    # Create and run the PoH leader node
    node = PoHLeaderNode(
        node_id=args.node_id,
        region=args.region,
        port=args.port,
        env_data_sources=env_data_sources,
        env_config_file=args.env_config or None,
        target_hash_rate=args.target_hash_rate,
        slot_duration=args.slot_duration
    )
    
    node.run()


if __name__ == "__main__":
    main()