#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PulseChain - Region Manager
==========================

This module implements the region management for PulseChain.
It handles the organization of nodes into geographic regions for efficient communication.
"""

import time
import hashlib
import json
import threading
import logging
import random
from typing import Dict, List, Optional, Any, Tuple, Set, Callable
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("region_manager")


@dataclass
class RegionInfo:
    """Information about a geographic region."""
    region_id: str
    name: str
    coordinator_id: Optional[str] = None
    node_count: int = 0
    active_nodes: Set[str] = field(default_factory=set)
    connected_regions: Set[str] = field(default_factory=set)
    creation_time: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)


@dataclass
class NodeRegionInfo:
    """Information about a node's region assignment."""
    node_id: str
    primary_region: str
    secondary_regions: Set[str] = field(default_factory=set)
    is_coordinator: bool = False
    join_time: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)


class RegionManager:
    """
    Region Manager for PulseChain.
    
    This class manages the organization of nodes into geographic regions
    for efficient communication and consensus.
    """
    
    def __init__(self, node_id: str, primary_region: str):
        """
        Initialize the region manager.
        
        Args:
            node_id: Identifier for this node
            primary_region: Primary geographic region for this node
        """
        self.node_id = node_id
        self.primary_region = primary_region
        
        # Regions
        self.regions: Dict[str, RegionInfo] = {}
        
        # Nodes
        self.nodes: Dict[str, NodeRegionInfo] = {}
        
        # Callbacks
        self.on_region_change_callbacks: List[Callable[[str, str], None]] = []
        self.on_coordinator_change_callbacks: List[Callable[[str, Optional[str]], None]] = []
        
        # Threading
        self.lock = threading.Lock()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # Create our primary region if it doesn't exist
        self.create_region(primary_region, primary_region)
        
        # Register ourselves
        self.register_node(node_id, primary_region)
        
        logger.info(f"Region Manager initialized for node {node_id} in region {primary_region}")
    
    def create_region(self, region_id: str, name: str) -> bool:
        """
        Create a new region.
        
        Args:
            region_id: Unique identifier for the region
            name: Human-readable name for the region
            
        Returns:
            True if the region was created, False if it already exists
        """
        with self.lock:
            if region_id in self.regions:
                logger.warning(f"Region {region_id} already exists")
                return False
            
            self.regions[region_id] = RegionInfo(
                region_id=region_id,
                name=name
            )
            
            logger.info(f"Created region {region_id} ({name})")
            return True
    
    def register_node(self, node_id: str, primary_region: str) -> bool:
        """
        Register a node in a region.
        
        Args:
            node_id: Identifier for the node
            primary_region: Primary geographic region for the node
            
        Returns:
            True if the node was registered, False otherwise
        """
        with self.lock:
            # Create the region if it doesn't exist
            if primary_region not in self.regions:
                self.create_region(primary_region, primary_region)
            
            # Check if node already exists
            if node_id in self.nodes:
                old_region = self.nodes[node_id].primary_region
                if old_region == primary_region:
                    # Just update last active time
                    self.nodes[node_id].last_active = time.time()
                    return True
                
                # Node is changing regions
                logger.info(f"Node {node_id} changing primary region from {old_region} to {primary_region}")
                
                # Remove from old region
                if old_region in self.regions:
                    self.regions[old_region].active_nodes.discard(node_id)
                    self.regions[old_region].node_count -= 1
                    self.regions[old_region].last_update = time.time()
                
                # Update node info
                self.nodes[node_id].primary_region = primary_region
                self.nodes[node_id].last_active = time.time()
                
                # Notify callbacks
                for callback in self.on_region_change_callbacks:
                    try:
                        callback(node_id, primary_region)
                    except Exception as e:
                        logger.error(f"Error in region change callback: {e}")
            else:
                # New node
                self.nodes[node_id] = NodeRegionInfo(
                    node_id=node_id,
                    primary_region=primary_region
                )
            
            # Add to region
            region = self.regions[primary_region]
            region.active_nodes.add(node_id)
            region.node_count += 1
            region.last_update = time.time()
            
            # Check if we need to assign a coordinator
            if region.coordinator_id is None:
                self._select_coordinator(primary_region)
            
            logger.info(f"Registered node {node_id} in region {primary_region}")
            return True
    
    def unregister_node(self, node_id: str) -> bool:
        """
        Unregister a node.
        
        Args:
            node_id: Identifier for the node
            
        Returns:
            True if the node was unregistered, False if it wasn't registered
        """
        with self.lock:
            if node_id not in self.nodes:
                logger.warning(f"Node {node_id} is not registered")
                return False
            
            node_info = self.nodes[node_id]
            primary_region = node_info.primary_region
            
            # Remove from primary region
            if primary_region in self.regions:
                region = self.regions[primary_region]
                region.active_nodes.discard(node_id)
                region.node_count -= 1
                region.last_update = time.time()
                
                # If this was the coordinator, select a new one
                if region.coordinator_id == node_id:
                    region.coordinator_id = None
                    self._select_coordinator(primary_region)
            
            # Remove from secondary regions
            for region_id in node_info.secondary_regions:
                if region_id in self.regions:
                    self.regions[region_id].active_nodes.discard(node_id)
                    self.regions[region_id].last_update = time.time()
            
            # Remove node
            del self.nodes[node_id]
            
            logger.info(f"Unregistered node {node_id} from region {primary_region}")
            return True
    
    def add_secondary_region(self, node_id: str, region_id: str) -> bool:
        """
        Add a node to a secondary region.
        
        Args:
            node_id: Identifier for the node
            region_id: Identifier for the secondary region
            
        Returns:
            True if the node was added to the region, False otherwise
        """
        with self.lock:
            if node_id not in self.nodes:
                logger.warning(f"Node {node_id} is not registered")
                return False
            
            if region_id not in self.regions:
                logger.warning(f"Region {region_id} does not exist")
                return False
            
            node_info = self.nodes[node_id]
            
            # Check if already in this region
            if region_id == node_info.primary_region:
                logger.warning(f"Region {region_id} is already the primary region for node {node_id}")
                return False
            
            if region_id in node_info.secondary_regions:
                logger.warning(f"Node {node_id} is already in secondary region {region_id}")
                return False
            
            # Add to secondary regions
            node_info.secondary_regions.add(region_id)
            
            # Add to region
            region = self.regions[region_id]
            region.active_nodes.add(node_id)
            region.last_update = time.time()
            
            logger.info(f"Added node {node_id} to secondary region {region_id}")
            return True
    
    def remove_secondary_region(self, node_id: str, region_id: str) -> bool:
        """
        Remove a node from a secondary region.
        
        Args:
            node_id: Identifier for the node
            region_id: Identifier for the secondary region
            
        Returns:
            True if the node was removed from the region, False otherwise
        """
        with self.lock:
            if node_id not in self.nodes:
                logger.warning(f"Node {node_id} is not registered")
                return False
            
            node_info = self.nodes[node_id]
            
            # Check if in this region
            if region_id not in node_info.secondary_regions:
                logger.warning(f"Node {node_id} is not in secondary region {region_id}")
                return False
            
            # Remove from secondary regions
            node_info.secondary_regions.remove(region_id)
            
            # Remove from region
            if region_id in self.regions:
                region = self.regions[region_id]
                region.active_nodes.discard(node_id)
                region.last_update = time.time()
            
            logger.info(f"Removed node {node_id} from secondary region {region_id}")
            return True
    
    def connect_regions(self, region_id1: str, region_id2: str) -> bool:
        """
        Connect two regions.
        
        Args:
            region_id1: Identifier for the first region
            region_id2: Identifier for the second region
            
        Returns:
            True if the regions were connected, False otherwise
        """
        with self.lock:
            if region_id1 not in self.regions:
                logger.warning(f"Region {region_id1} does not exist")
                return False
            
            if region_id2 not in self.regions:
                logger.warning(f"Region {region_id2} does not exist")
                return False
            
            if region_id1 == region_id2:
                logger.warning(f"Cannot connect region {region_id1} to itself")
                return False
            
            # Connect regions
            self.regions[region_id1].connected_regions.add(region_id2)
            self.regions[region_id2].connected_regions.add(region_id1)
            
            # Update timestamps
            self.regions[region_id1].last_update = time.time()
            self.regions[region_id2].last_update = time.time()
            
            logger.info(f"Connected regions {region_id1} and {region_id2}")
            return True
    
    def disconnect_regions(self, region_id1: str, region_id2: str) -> bool:
        """
        Disconnect two regions.
        
        Args:
            region_id1: Identifier for the first region
            region_id2: Identifier for the second region
            
        Returns:
            True if the regions were disconnected, False otherwise
        """
        with self.lock:
            if region_id1 not in self.regions:
                logger.warning(f"Region {region_id1} does not exist")
                return False
            
            if region_id2 not in self.regions:
                logger.warning(f"Region {region_id2} does not exist")
                return False
            
            # Disconnect regions
            self.regions[region_id1].connected_regions.discard(region_id2)
            self.regions[region_id2].connected_regions.discard(region_id1)
            
            # Update timestamps
            self.regions[region_id1].last_update = time.time()
            self.regions[region_id2].last_update = time.time()
            
            logger.info(f"Disconnected regions {region_id1} and {region_id2}")
            return True
    
    def _select_coordinator(self, region_id: str) -> Optional[str]:
        """
        Select a coordinator for a region.
        
        Args:
            region_id: Identifier for the region
            
        Returns:
            The ID of the selected coordinator, or None if no coordinator could be selected
        """
        with self.lock:
            if region_id not in self.regions:
                logger.warning(f"Region {region_id} does not exist")
                return None
            
            region = self.regions[region_id]
            
            # If there are no active nodes, there can be no coordinator
            if not region.active_nodes:
                region.coordinator_id = None
                return None
            
            # If there's only one node, it becomes the coordinator
            if len(region.active_nodes) == 1:
                coordinator_id = next(iter(region.active_nodes))
                region.coordinator_id = coordinator_id
                
                # Update node info
                if coordinator_id in self.nodes:
                    self.nodes[coordinator_id].is_coordinator = True
                
                # Notify callbacks
                for callback in self.on_coordinator_change_callbacks:
                    try:
                        callback(region_id, coordinator_id)
                    except Exception as e:
                        logger.error(f"Error in coordinator change callback: {e}")
                
                logger.info(f"Selected node {coordinator_id} as coordinator for region {region_id}")
                return coordinator_id
            
            # Otherwise, select based on node ID (deterministic)
            # In a real implementation, this would use more sophisticated criteria
            coordinator_id = sorted(region.active_nodes)[0]
            old_coordinator = region.coordinator_id
            region.coordinator_id = coordinator_id
            
            # Update node info
            for node_id in region.active_nodes:
                if node_id in self.nodes:
                    self.nodes[node_id].is_coordinator = (node_id == coordinator_id)
            
            # Notify callbacks if coordinator changed
            if old_coordinator != coordinator_id:
                for callback in self.on_coordinator_change_callbacks:
                    try:
                        callback(region_id, coordinator_id)
                    except Exception as e:
                        logger.error(f"Error in coordinator change callback: {e}")
                
                logger.info(f"Selected node {coordinator_id} as coordinator for region {region_id}")
            
            return coordinator_id
    
    def get_region_nodes(self, region_id: str) -> List[str]:
        """
        Get a list of nodes in a region.
        
        Args:
            region_id: Identifier for the region
            
        Returns:
            List of node IDs in the region
        """
        with self.lock:
            if region_id not in self.regions:
                return []
            
            return list(self.regions[region_id].active_nodes)
    
    def get_node_regions(self, node_id: str) -> Tuple[Optional[str], List[str]]:
        """
        Get the regions a node belongs to.
        
        Args:
            node_id: Identifier for the node
            
        Returns:
            Tuple of (primary_region, secondary_regions)
        """
        with self.lock:
            if node_id not in self.nodes:
                return None, []
            
            node_info = self.nodes[node_id]
            return node_info.primary_region, list(node_info.secondary_regions)
    
    def get_region_coordinator(self, region_id: str) -> Optional[str]:
        """
        Get the coordinator for a region.
        
        Args:
            region_id: Identifier for the region
            
        Returns:
            The ID of the coordinator, or None if there is no coordinator
        """
        with self.lock:
            if region_id not in self.regions:
                return None
            
            return self.regions[region_id].coordinator_id
    
    def is_coordinator(self, node_id: str) -> bool:
        """
        Check if a node is a coordinator for any region.
        
        Args:
            node_id: Identifier for the node
            
        Returns:
            True if the node is a coordinator, False otherwise
        """
        with self.lock:
            if node_id not in self.nodes:
                return False
            
            return self.nodes[node_id].is_coordinator
    
    def get_connected_regions(self, region_id: str) -> List[str]:
        """
        Get a list of regions connected to a region.
        
        Args:
            region_id: Identifier for the region
            
        Returns:
            List of connected region IDs
        """
        with self.lock:
            if region_id not in self.regions:
                return []
            
            return list(self.regions[region_id].connected_regions)
    
    def on_region_change(self, callback: Callable[[str, str], None]) -> None:
        """
        Register a callback to be called when a node changes regions.
        
        Args:
            callback: The callback function (node_id, new_region)
        """
        self.on_region_change_callbacks.append(callback)
    
    def on_coordinator_change(self, callback: Callable[[str, Optional[str]], None]) -> None:
        """
        Register a callback to be called when a region's coordinator changes.
        
        Args:
            callback: The callback function (region_id, new_coordinator_id)
        """
        self.on_coordinator_change_callbacks.append(callback)
    
    def start(self) -> None:
        """Start the region manager."""
        if self.running:
            logger.warning("Region Manager is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        
        logger.info("Region Manager started")
    
    def stop(self) -> None:
        """Stop the region manager."""
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
        
        logger.info("Region Manager stopped")
    
    def _run(self) -> None:
        """Run the region manager."""
        while self.running:
            try:
                # Check for inactive nodes
                self._check_inactive_nodes()
                
                # Check for regions without coordinators
                self._check_coordinators()
            except Exception as e:
                logger.error(f"Error in region manager: {e}")
            
            # Sleep for a bit
            time.sleep(5.0)
    
    def _check_inactive_nodes(self) -> None:
        """Check for inactive nodes and remove them."""
        with self.lock:
            current_time = time.time()
            inactive_timeout = 60.0  # 1 minute
            
            inactive_nodes = []
            for node_id, node_info in self.nodes.items():
                if current_time - node_info.last_active > inactive_timeout:
                    inactive_nodes.append(node_id)
            
            for node_id in inactive_nodes:
                logger.info(f"Removing inactive node {node_id}")
                self.unregister_node(node_id)
    
    def _check_coordinators(self) -> None:
        """Check for regions without coordinators and select new ones."""
        with self.lock:
            for region_id, region in self.regions.items():
                if region.coordinator_id is None and region.active_nodes:
                    self._select_coordinator(region_id)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the region manager.
        
        Returns:
            A dictionary with status information
        """
        with self.lock:
            return {
                "node_id": self.node_id,
                "primary_region": self.primary_region,
                "is_coordinator": self.is_coordinator(self.node_id),
                "regions": {
                    region_id: {
                        "name": region.name,
                        "coordinator": region.coordinator_id,
                        "node_count": region.node_count,
                        "active_nodes": len(region.active_nodes),
                        "connected_regions": len(region.connected_regions)
                    }
                    for region_id, region in self.regions.items()
                },
                "nodes": len(self.nodes)
            }


# Example usage
if __name__ == "__main__":
    # Create a region manager
    region_manager = RegionManager(
        node_id="node1",
        primary_region="us-west"
    )
    
    # Create some regions
    region_manager.create_region("us-east", "US East")
    region_manager.create_region("eu-west", "EU West")
    region_manager.create_region("ap-east", "Asia Pacific East")
    
    # Connect regions
    region_manager.connect_regions("us-west", "us-east")
    region_manager.connect_regions("us-east", "eu-west")
    region_manager.connect_regions("eu-west", "ap-east")
    
    # Register some nodes
    for i in range(2, 11):
        if i < 4:
            region = "us-west"
        elif i < 7:
            region = "us-east"
        elif i < 9:
            region = "eu-west"
        else:
            region = "ap-east"
        
        region_manager.register_node(f"node{i}", region)
    
    # Add some secondary regions
    region_manager.add_secondary_region("node2", "us-east")
    region_manager.add_secondary_region("node5", "us-west")
    region_manager.add_secondary_region("node8", "ap-east")
    
    # Define callbacks
    def on_region_change(node_id: str, new_region: str):
        print(f"Node {node_id} changed to region {new_region}")
    
    def on_coordinator_change(region_id: str, new_coordinator: Optional[str]):
        print(f"Region {region_id} coordinator changed to {new_coordinator}")
    
    region_manager.on_region_change(on_region_change)
    region_manager.on_coordinator_change(on_coordinator_change)
    
    # Start the region manager
    region_manager.start()
    
    try:
        # Print initial status
        status = region_manager.get_status()
        print("\nInitial status:")
        print(f"Node: {status['node_id']} in region {status['primary_region']}")
        print(f"Is coordinator: {status['is_coordinator']}")
        print("\nRegions:")
        for region_id, region in status['regions'].items():
            print(f"  {region_id} ({region['name']}): {region['node_count']} nodes, coordinator: {region['coordinator']}")
        
        # Make some changes
        print("\nMaking changes...")
        region_manager.register_node("node11", "ap-east")
        region_manager.unregister_node("node3")
        region_manager.register_node("node5", "eu-west")  # Change region
        
        # Wait for changes to propagate
        time.sleep(1.0)
        
        # Print final status
        status = region_manager.get_status()
        print("\nFinal status:")
        print(f"Node: {status['node_id']} in region {status['primary_region']}")
        print(f"Is coordinator: {status['is_coordinator']}")
        print("\nRegions:")
        for region_id, region in status['regions'].items():
            print(f"  {region_id} ({region['name']}): {region['node_count']} nodes, coordinator: {region['coordinator']}")
        
        # Print node regions
        print("\nNode regions:")
        for i in range(1, 12):
            node_id = f"node{i}"
            primary, secondary = region_manager.get_node_regions(node_id)
            if primary:
                print(f"  {node_id}: primary={primary}, secondary={secondary}")
    
    finally:
        # Stop the region manager
        region_manager.stop()