#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PulseChain - Solana Data Source
==============================

This module provides functionality to fetch data from the Solana blockchain
to be used as environmental data in the PulseChain consensus mechanism.
"""

import time
import json
import logging
import threading
from typing import Dict, List, Optional, Any, Tuple, Set, Callable, Union
import requests
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("solana_data_source")


@dataclass
class SolanaClusterInfo:
    """Information about a Solana cluster."""
    name: str
    rpc_url: str
    ws_url: Optional[str] = None
    is_active: bool = True
    last_check: float = field(default_factory=time.time)
    response_time: float = 0.0


class SolanaDataSource:
    """
    Solana Data Source for PulseChain.
    
    This class fetches data from the Solana blockchain to be used as
    environmental data in the PulseChain consensus mechanism.
    """
    
    def __init__(self, 
                 primary_cluster: str = "mainnet-beta",
                 update_interval: float = 10.0,
                 max_retries: int = 3):
        """
        Initialize the Solana data source.
        
        Args:
            primary_cluster: The primary Solana cluster to use
            update_interval: How often to update data (in seconds)
            max_retries: Maximum number of retries for failed requests
        """
        self.primary_cluster = primary_cluster
        self.update_interval = update_interval
        self.max_retries = max_retries
        
        # Solana clusters
        self.clusters: Dict[str, SolanaClusterInfo] = {
            "mainnet-beta": SolanaClusterInfo(
                name="Mainnet Beta",
                rpc_url="https://api.mainnet-beta.solana.com",
                ws_url="wss://api.mainnet-beta.solana.com"
            ),
            "testnet": SolanaClusterInfo(
                name="Testnet",
                rpc_url="https://api.testnet.solana.com",
                ws_url="wss://api.testnet.solana.com"
            ),
            "devnet": SolanaClusterInfo(
                name="Devnet",
                rpc_url="https://api.devnet.solana.com",
                ws_url="wss://api.devnet.solana.com"
            ),
            "localnet": SolanaClusterInfo(
                name="Localnet",
                rpc_url="http://localhost:8899",
                ws_url="ws://localhost:8900"
            )
        }
        
        # Data storage
        self.latest_data: Dict[str, Any] = {}
        self.historical_data: List[Dict[str, Any]] = []
        
        # Callbacks
        self.on_data_updated_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        
        # Threading
        self.lock = threading.Lock()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        logger.info(f"Solana Data Source initialized with primary cluster: {primary_cluster}")
    
    def add_custom_cluster(self, 
                          cluster_id: str, 
                          name: str, 
                          rpc_url: str,
                          ws_url: Optional[str] = None) -> bool:
        """
        Add a custom Solana cluster.
        
        Args:
            cluster_id: Unique identifier for the cluster
            name: Human-readable name for the cluster
            rpc_url: RPC URL for the cluster
            ws_url: WebSocket URL for the cluster
            
        Returns:
            True if the cluster was added successfully, False otherwise
        """
        with self.lock:
            if cluster_id in self.clusters:
                logger.warning(f"Cluster {cluster_id} already exists")
                return False
            
            self.clusters[cluster_id] = SolanaClusterInfo(
                name=name,
                rpc_url=rpc_url,
                ws_url=ws_url
            )
            
            logger.info(f"Added custom Solana cluster: {cluster_id} ({name})")
            return True
    
    def remove_cluster(self, cluster_id: str) -> bool:
        """
        Remove a Solana cluster.
        
        Args:
            cluster_id: Identifier of the cluster to remove
            
        Returns:
            True if the cluster was removed, False if it didn't exist
        """
        with self.lock:
            if cluster_id not in self.clusters:
                logger.warning(f"Cluster {cluster_id} does not exist")
                return False
            
            # Don't allow removing the primary cluster
            if cluster_id == self.primary_cluster:
                logger.warning(f"Cannot remove primary cluster {cluster_id}")
                return False
            
            del self.clusters[cluster_id]
            
            logger.info(f"Removed Solana cluster: {cluster_id}")
            return True
    
    def set_primary_cluster(self, cluster_id: str) -> bool:
        """
        Set the primary Solana cluster.
        
        Args:
            cluster_id: Identifier of the cluster to set as primary
            
        Returns:
            True if the primary cluster was set, False if the cluster doesn't exist
        """
        with self.lock:
            if cluster_id not in self.clusters:
                logger.warning(f"Cluster {cluster_id} does not exist")
                return False
            
            self.primary_cluster = cluster_id
            
            logger.info(f"Set primary Solana cluster to {cluster_id}")
            return True
    
    def get_cluster_info(self, cluster_id: Optional[str] = None) -> Optional[SolanaClusterInfo]:
        """
        Get information about a Solana cluster.
        
        Args:
            cluster_id: Identifier of the cluster, or None for the primary cluster
            
        Returns:
            Cluster information, or None if the cluster doesn't exist
        """
        with self.lock:
            if cluster_id is None:
                cluster_id = self.primary_cluster
            
            return self.clusters.get(cluster_id)
    
    def _make_rpc_request(self, 
                         method: str, 
                         params: Optional[List[Any]] = None,
                         cluster_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Make an RPC request to a Solana cluster.
        
        Args:
            method: The RPC method to call
            params: Parameters for the method
            cluster_id: Identifier of the cluster, or None for the primary cluster
            
        Returns:
            The response, or None if the request failed
        """
        if cluster_id is None:
            cluster_id = self.primary_cluster
        
        cluster_info = self.get_cluster_info(cluster_id)
        if not cluster_info:
            logger.warning(f"Cluster {cluster_id} does not exist")
            return None
        
        if not cluster_info.is_active:
            logger.warning(f"Cluster {cluster_id} is not active")
            return None
        
        rpc_url = cluster_info.rpc_url
        
        # Prepare request
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method
        }
        
        if params:
            request_data["params"] = params
        
        # Make request with retries
        for retry in range(self.max_retries):
            try:
                start_time = time.time()
                response = requests.post(
                    rpc_url,
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                response_time = time.time() - start_time
                
                # Update cluster info
                with self.lock:
                    cluster_info.last_check = time.time()
                    cluster_info.response_time = response_time
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        if "result" in result:
                            return result
                        elif "error" in result:
                            logger.warning(f"RPC error: {result['error']}")
                    except Exception as e:
                        logger.error(f"Error parsing RPC response: {e}")
                else:
                    logger.warning(f"RPC request failed with status {response.status_code}")
                
            except Exception as e:
                logger.error(f"Error making RPC request: {e}")
            
            # If we get here, the request failed
            logger.warning(f"Retrying RPC request ({retry+1}/{self.max_retries})...")
            time.sleep(1.0)
        
        # If we get here, all retries failed
        logger.error(f"All RPC request retries failed")
        
        # Mark cluster as inactive
        with self.lock:
            cluster_info.is_active = False
        
        return None
    
    def get_slot(self, cluster_id: Optional[str] = None) -> Optional[int]:
        """
        Get the current slot number.
        
        Args:
            cluster_id: Identifier of the cluster, or None for the primary cluster
            
        Returns:
            The current slot number, or None if the request failed
        """
        response = self._make_rpc_request("getSlot", cluster_id=cluster_id)
        if response and "result" in response:
            return response["result"]
        return None
    
    def get_block_time(self, slot: int, cluster_id: Optional[str] = None) -> Optional[int]:
        """
        Get the block time for a slot.
        
        Args:
            slot: The slot number
            cluster_id: Identifier of the cluster, or None for the primary cluster
            
        Returns:
            The block time (Unix timestamp), or None if the request failed
        """
        response = self._make_rpc_request("getBlockTime", [slot], cluster_id=cluster_id)
        if response and "result" in response:
            return response["result"]
        return None
    
    def get_recent_performance(self, cluster_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get recent performance samples.
        
        Args:
            cluster_id: Identifier of the cluster, or None for the primary cluster
            
        Returns:
            Performance data, or None if the request failed
        """
        response = self._make_rpc_request("getRecentPerformanceSamples", [10], cluster_id=cluster_id)
        if response and "result" in response:
            return response["result"]
        return None
    
    def get_block_production(self, cluster_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get block production information.
        
        Args:
            cluster_id: Identifier of the cluster, or None for the primary cluster
            
        Returns:
            Block production data, or None if the request failed
        """
        response = self._make_rpc_request("getBlockProduction", cluster_id=cluster_id)
        if response and "result" in response:
            return response["result"]
        return None
    
    def get_health(self, cluster_id: Optional[str] = None) -> bool:
        """
        Check if the cluster is healthy.
        
        Args:
            cluster_id: Identifier of the cluster, or None for the primary cluster
            
        Returns:
            True if the cluster is healthy, False otherwise
        """
        response = self._make_rpc_request("getHealth", cluster_id=cluster_id)
        if response and "result" in response and response["result"] == "ok":
            return True
        return False
    
    def get_version(self, cluster_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get the version of the cluster.
        
        Args:
            cluster_id: Identifier of the cluster, or None for the primary cluster
            
        Returns:
            Version information, or None if the request failed
        """
        response = self._make_rpc_request("getVersion", cluster_id=cluster_id)
        if response and "result" in response:
            return response["result"]
        return None
    
    def collect_data(self) -> Dict[str, Any]:
        """
        Collect data from the Solana blockchain.
        
        Returns:
            Collected data
        """
        data = {
            "timestamp": time.time(),
            "source": "solana",
            "cluster": self.primary_cluster
        }
        
        # Get slot
        slot = self.get_slot()
        if slot is not None:
            data["slot"] = slot
            
            # Get block time
            block_time = self.get_block_time(slot)
            if block_time is not None:
                data["block_time"] = block_time
        
        # Get performance
        performance = self.get_recent_performance()
        if performance is not None:
            data["performance"] = performance
        
        # Get health
        health = self.get_health()
        data["health"] = health
        
        # Get version
        version = self.get_version()
        if version is not None:
            data["version"] = version
        
        # Store data
        with self.lock:
            self.latest_data = data
            self.historical_data.append(data)
            
            # Limit the size of historical data
            if len(self.historical_data) > 1000:
                self.historical_data = self.historical_data[-1000:]
        
        # Notify callbacks
        for callback in self.on_data_updated_callbacks:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error in data updated callback: {e}")
        
        return data
    
    def get_latest_data(self) -> Dict[str, Any]:
        """
        Get the latest collected data.
        
        Returns:
            The latest data
        """
        with self.lock:
            return dict(self.latest_data)
    
    def get_historical_data(self, count: int = 100) -> List[Dict[str, Any]]:
        """
        Get historical data.
        
        Args:
            count: Maximum number of data points to return
            
        Returns:
            List of historical data points
        """
        with self.lock:
            return list(self.historical_data[-count:])
    
    def on_data_updated(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Register a callback to be called when data is updated.
        
        Args:
            callback: The callback function
        """
        self.on_data_updated_callbacks.append(callback)
    
    def start(self) -> None:
        """Start the Solana data source."""
        if self.running:
            logger.warning("Solana Data Source is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        
        logger.info("Solana Data Source started")
    
    def stop(self) -> None:
        """Stop the Solana data source."""
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
        
        logger.info("Solana Data Source stopped")
    
    def _run(self) -> None:
        """Run the Solana data source."""
        while self.running:
            try:
                # Collect data
                self.collect_data()
                
            except Exception as e:
                logger.error(f"Error collecting Solana data: {e}")
            
            # Sleep until next update
            time.sleep(self.update_interval)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the Solana data source.
        
        Returns:
            A dictionary with status information
        """
        with self.lock:
            return {
                "primary_cluster": self.primary_cluster,
                "clusters": {
                    cluster_id: {
                        "name": cluster.name,
                        "is_active": cluster.is_active,
                        "last_check": cluster.last_check,
                        "response_time": cluster.response_time
                    }
                    for cluster_id, cluster in self.clusters.items()
                },
                "update_interval": self.update_interval,
                "historical_data_points": len(self.historical_data),
                "latest_data_timestamp": self.latest_data.get("timestamp")
            }


# Example usage
if __name__ == "__main__":
    # Create a Solana data source
    solana_source = SolanaDataSource(
        primary_cluster="mainnet-beta",
        update_interval=10.0
    )
    
    # Define a callback
    def on_data_updated(data: Dict[str, Any]):
        print(f"Received new Solana data: slot={data.get('slot')}, time={data.get('timestamp')}")
    
    solana_source.on_data_updated(on_data_updated)
    
    # Start the data source
    solana_source.start()
    
    try:
        # Run for a while
        print("Collecting Solana data for 30 seconds...")
        for _ in range(3):
            time.sleep(10)
            
            # Print status
            status = solana_source.get_status()
            print(f"\nStatus: primary_cluster={status['primary_cluster']}")
            print(f"Historical data points: {status['historical_data_points']}")
            
            # Print latest data
            latest = solana_source.get_latest_data()
            if latest:
                print(f"Latest data:")
                print(f"  Slot: {latest.get('slot')}")
                print(f"  Block time: {latest.get('block_time')}")
                print(f"  Health: {latest.get('health')}")
                if 'version' in latest:
                    print(f"  Version: {latest.get('version', {}).get('solana-core')}")
    
    finally:
        # Stop the data source
        solana_source.stop()