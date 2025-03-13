#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PulseChain - Region Synchronization
=================================

This module implements the synchronization between regions in PulseChain.
It handles the communication and data exchange between different geographic regions.
"""

import time
import hashlib
import json
import threading
import logging
import random
from typing import Dict, List, Optional, Any, Tuple, Set, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

from ..core.region_manager import RegionManager
from ..consensus.poh import PoHConsensus, PoHSlot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("region_sync")


@dataclass
class SyncMessage:
    """A message exchanged between regions."""
    source_region: str
    target_region: str
    message_type: str
    data: Dict[str, Any]
    timestamp: float
    message_id: str = field(default_factory=lambda: hashlib.sha256(str(time.time() + random.random()).encode()).hexdigest()[:16])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source_region": self.source_region,
            "target_region": self.target_region,
            "message_type": self.message_type,
            "data": self.data,
            "timestamp": self.timestamp,
            "message_id": self.message_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SyncMessage':
        """Create from dictionary after deserialization."""
        return cls(
            source_region=data["source_region"],
            target_region=data["target_region"],
            message_type=data["message_type"],
            data=data["data"],
            timestamp=data["timestamp"],
            message_id=data["message_id"]
        )


class RegionSync:
    """
    Region Synchronization for PulseChain.
    
    This class handles the synchronization between different geographic regions,
    including data exchange and consensus coordination.
    """
    
    def __init__(self, 
                 region_manager: RegionManager,
                 poh_consensus: PoHConsensus,
                 sync_interval: float = 1.0):  # 1 second
        """
        Initialize the region synchronization.
        
        Args:
            region_manager: The region manager
            poh_consensus: The PoH consensus mechanism
            sync_interval: Interval between synchronization attempts (in seconds)
        """
        self.region_manager = region_manager
        self.poh_consensus = poh_consensus
        self.sync_interval = sync_interval
        
        # Message queues
        self.outgoing_messages: List[SyncMessage] = []
        self.incoming_messages: List[SyncMessage] = []
        self.processed_message_ids: Set[str] = set()
        
        # Callbacks
        self.message_handlers: Dict[str, Callable[[SyncMessage], None]] = {}
        
        # Threading
        self.lock = threading.Lock()
        self.running = False
        self.sync_thread: Optional[threading.Thread] = None
        
        # Register default message handlers
        self._register_default_handlers()
        
        logger.info(f"Region Sync initialized for region {region_manager.primary_region}")
    
    def _register_default_handlers(self) -> None:
        """Register default message handlers."""
        self.register_message_handler("poh_slot", self._handle_poh_slot)
        self.register_message_handler("poh_chain", self._handle_poh_chain)
        self.register_message_handler("region_info", self._handle_region_info)
        self.register_message_handler("node_info", self._handle_node_info)
    
    def register_message_handler(self, 
                               message_type: str, 
                               handler: Callable[[SyncMessage], None]) -> None:
        """
        Register a handler for a specific message type.
        
        Args:
            message_type: The type of message to handle
            handler: The handler function
        """
        self.message_handlers[message_type] = handler
        logger.debug(f"Registered handler for message type: {message_type}")
    
    def send_message(self, message: SyncMessage) -> bool:
        """
        Send a message to another region.
        
        Args:
            message: The message to send
            
        Returns:
            True if the message was queued for sending, False otherwise
        """
        with self.lock:
            # Check if target region exists
            if message.target_region not in self.region_manager.regions:
                logger.warning(f"Target region {message.target_region} does not exist")
                return False
            
            # Check if regions are connected
            if message.target_region not in self.region_manager.get_connected_regions(message.source_region):
                logger.warning(f"Regions {message.source_region} and {message.target_region} are not connected")
                return False
            
            # Add to outgoing queue
            self.outgoing_messages.append(message)
            
            logger.debug(f"Queued message {message.message_id} for sending to {message.target_region}")
            return True
    
    def broadcast_message(self, 
                         message_type: str, 
                         data: Dict[str, Any],
                         exclude_regions: Optional[List[str]] = None) -> int:
        """
        Broadcast a message to all connected regions.
        
        Args:
            message_type: The type of message to broadcast
            data: The message data
            exclude_regions: Optional list of regions to exclude from the broadcast
            
        Returns:
            Number of messages queued for sending
        """
        with self.lock:
            source_region = self.region_manager.primary_region
            connected_regions = self.region_manager.get_connected_regions(source_region)
            
            if exclude_regions:
                connected_regions = [r for r in connected_regions if r not in exclude_regions]
            
            count = 0
            for target_region in connected_regions:
                message = SyncMessage(
                    source_region=source_region,
                    target_region=target_region,
                    message_type=message_type,
                    data=data,
                    timestamp=time.time()
                )
                
                if self.send_message(message):
                    count += 1
            
            logger.debug(f"Broadcast {message_type} message to {count} regions")
            return count
    
    def process_message(self, message: SyncMessage) -> bool:
        """
        Process a received message.
        
        Args:
            message: The message to process
            
        Returns:
            True if the message was processed successfully, False otherwise
        """
        with self.lock:
            # Check if message has already been processed
            if message.message_id in self.processed_message_ids:
                logger.debug(f"Message {message.message_id} has already been processed")
                return False
            
            # Check if message is for this region
            if message.target_region != self.region_manager.primary_region:
                logger.warning(f"Message {message.message_id} is not for this region")
                return False
            
            # Check if source region is connected
            if message.source_region not in self.region_manager.get_connected_regions(message.target_region):
                logger.warning(f"Source region {message.source_region} is not connected")
                return False
            
            # Check if message is too old
            if time.time() - message.timestamp > 60.0:  # 1 minute
                logger.warning(f"Message {message.message_id} is too old")
                return False
            
            # Process message based on type
            if message.message_type in self.message_handlers:
                try:
                    self.message_handlers[message.message_type](message)
                    
                    # Mark as processed
                    self.processed_message_ids.add(message.message_id)
                    
                    # Limit the size of processed_message_ids
                    if len(self.processed_message_ids) > 10000:
                        self.processed_message_ids = set(list(self.processed_message_ids)[-5000:])
                    
                    logger.debug(f"Processed message {message.message_id} of type {message.message_type}")
                    return True
                    
                except Exception as e:
                    logger.error(f"Error processing message {message.message_id}: {e}")
                    return False
            else:
                logger.warning(f"No handler for message type: {message.message_type}")
                return False
    
    def _handle_poh_slot(self, message: SyncMessage) -> None:
        """
        Handle a PoH slot message.
        
        Args:
            message: The message to handle
        """
        # Extract slot data
        slot_data = message.data.get("slot")
        if not slot_data:
            logger.warning("No slot data in message")
            return
        
        # Check if we already have this slot
        slot_number = slot_data.get("slot_number")
        if slot_number is None:
            logger.warning("No slot number in slot data")
            return
        
        existing_slot = self.poh_consensus.get_slot(slot_number)
        if existing_slot and existing_slot.is_finalized:
            logger.debug(f"Slot {slot_number} is already finalized")
            return
        
        # If we don't have this slot or it's not finalized, request the PoH chain
        if not existing_slot or not existing_slot.is_finalized:
            # Request PoH chain from the source region
            self.send_message(SyncMessage(
                source_region=self.region_manager.primary_region,
                target_region=message.source_region,
                message_type="poh_chain_request",
                data={
                    "start_slot": max(0, slot_number - 10),
                    "end_slot": slot_number
                },
                timestamp=time.time()
            ))
    
    def _handle_poh_chain(self, message: SyncMessage) -> None:
        """
        Handle a PoH chain message.
        
        Args:
            message: The message to handle
        """
        # Extract chain data
        chain_data = message.data.get("chain")
        if not chain_data:
            logger.warning("No chain data in message")
            return
        
        # Import the chain into our PoH consensus
        # In a real implementation, this would validate and merge the chain
        logger.info(f"Received PoH chain from {message.source_region} with {len(chain_data)} slots")
        
        # For now, just log the received chain
        for slot_data in chain_data:
            slot_number = slot_data.get("slot_number")
            if slot_number is not None:
                logger.debug(f"Received slot {slot_number} from {message.source_region}")
    
    def _handle_region_info(self, message: SyncMessage) -> None:
        """
        Handle a region info message.
        
        Args:
            message: The message to handle
        """
        # Extract region info
        region_info = message.data.get("region_info")
        if not region_info:
            logger.warning("No region info in message")
            return
        
        # Update our region manager with the received info
        region_id = region_info.get("region_id")
        if not region_id:
            logger.warning("No region ID in region info")
            return
        
        # Create the region if it doesn't exist
        if region_id not in self.region_manager.regions:
            name = region_info.get("name", region_id)
            self.region_manager.create_region(region_id, name)
        
        # Connect to the region if not already connected
        if region_id not in self.region_manager.get_connected_regions(self.region_manager.primary_region):
            self.region_manager.connect_regions(self.region_manager.primary_region, region_id)
        
        logger.info(f"Updated region info for {region_id}")
    
    def _handle_node_info(self, message: SyncMessage) -> None:
        """
        Handle a node info message.
        
        Args:
            message: The message to handle
        """
        # Extract node info
        node_info_list = message.data.get("node_info")
        if not node_info_list:
            logger.warning("No node info in message")
            return
        
        # Update our region manager with the received info
        for node_info in node_info_list:
            node_id = node_info.get("node_id")
            primary_region = node_info.get("primary_region")
            
            if not node_id or not primary_region:
                logger.warning("Missing node ID or primary region in node info")
                continue
            
            # Register the node
            self.region_manager.register_node(node_id, primary_region)
            
            # Add secondary regions
            secondary_regions = node_info.get("secondary_regions", [])
            for region_id in secondary_regions:
                self.region_manager.add_secondary_region(node_id, region_id)
        
        logger.info(f"Updated info for {len(node_info_list)} nodes from {message.source_region}")
    
    def sync_poh_slots(self) -> None:
        """Synchronize PoH slots with connected regions."""
        # Get the latest finalized slot
        latest_slot = self.poh_consensus.get_latest_finalized_slot()
        if not latest_slot:
            logger.debug("No finalized slots to sync")
            return
        
        # Broadcast the latest slot to all connected regions
        self.broadcast_message(
            message_type="poh_slot",
            data={
                "slot": {
                    "slot_number": latest_slot.slot_number,
                    "leader_id": latest_slot.leader_id,
                    "start_time": latest_slot.start_time,
                    "end_time": latest_slot.end_time,
                    "is_finalized": latest_slot.is_finalized,
                    "confirmation_count": len(latest_slot.confirmations)
                }
            }
        )
    
    def sync_region_info(self) -> None:
        """Synchronize region information with connected regions."""
        # Get our region info
        region_id = self.region_manager.primary_region
        region = self.region_manager.regions.get(region_id)
        if not region:
            logger.warning(f"Region {region_id} not found")
            return
        
        # Broadcast region info to all connected regions
        self.broadcast_message(
            message_type="region_info",
            data={
                "region_info": {
                    "region_id": region_id,
                    "name": region.name,
                    "coordinator_id": region.coordinator_id,
                    "node_count": region.node_count,
                    "active_node_count": len(region.active_nodes),
                    "connected_regions": list(region.connected_regions)
                }
            }
        )
    
    def sync_node_info(self) -> None:
        """Synchronize node information with connected regions."""
        # Get nodes in our region
        region_id = self.region_manager.primary_region
        nodes = self.region_manager.get_region_nodes(region_id)
        
        # Prepare node info
        node_info_list = []
        for node_id in nodes:
            primary_region, secondary_regions = self.region_manager.get_node_regions(node_id)
            if primary_region:
                node_info_list.append({
                    "node_id": node_id,
                    "primary_region": primary_region,
                    "secondary_regions": secondary_regions,
                    "is_coordinator": self.region_manager.is_coordinator(node_id)
                })
        
        # Broadcast node info to all connected regions
        if node_info_list:
            self.broadcast_message(
                message_type="node_info",
                data={
                    "node_info": node_info_list
                }
            )
    
    def start(self) -> None:
        """Start the region synchronization."""
        if self.running:
            logger.warning("Region Sync is already running")
            return
        
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_thread, daemon=True)
        self.sync_thread.start()
        
        logger.info("Region Sync started")
    
    def stop(self) -> None:
        """Stop the region synchronization."""
        self.running = False
        
        if self.sync_thread:
            self.sync_thread.join(timeout=2.0)
            self.sync_thread = None
        
        logger.info("Region Sync stopped")
    
    def _sync_thread(self) -> None:
        """Synchronization thread."""
        # Counters for staggering different types of sync
        poh_counter = 0
        region_counter = 0
        node_counter = 0
        
        while self.running:
            try:
                # Process incoming messages
                with self.lock:
                    messages_to_process = list(self.incoming_messages)
                    self.incoming_messages = []
                
                for message in messages_to_process:
                    self.process_message(message)
                
                # Send outgoing messages
                with self.lock:
                    messages_to_send = list(self.outgoing_messages)
                    self.outgoing_messages = []
                
                for message in messages_to_send:
                    # In a real implementation, this would send the message over the network
                    # For now, we just simulate sending by adding it to the incoming queue
                    # of the target region (which is actually the same instance in this simulation)
                    with self.lock:
                        self.incoming_messages.append(message)
                    
                    logger.debug(f"Sent message {message.message_id} to {message.target_region}")
                
                # Perform periodic synchronization
                poh_counter += 1
                if poh_counter >= 1:  # Sync PoH every interval
                    self.sync_poh_slots()
                    poh_counter = 0
                
                region_counter += 1
                if region_counter >= 5:  # Sync region info every 5 intervals
                    self.sync_region_info()
                    region_counter = 0
                
                node_counter += 1
                if node_counter >= 10:  # Sync node info every 10 intervals
                    self.sync_node_info()
                    node_counter = 0
                
            except Exception as e:
                logger.error(f"Error in sync thread: {e}")
            
            # Sleep until next sync
            time.sleep(self.sync_interval)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the region synchronization.
        
        Returns:
            A dictionary with status information
        """
        with self.lock:
            return {
                "primary_region": self.region_manager.primary_region,
                "connected_regions": self.region_manager.get_connected_regions(self.region_manager.primary_region),
                "outgoing_messages": len(self.outgoing_messages),
                "incoming_messages": len(self.incoming_messages),
                "processed_messages": len(self.processed_message_ids),
                "sync_interval": self.sync_interval
            }


# Example usage
if __name__ == "__main__":
    from ..core.poh_generator import PoHGenerator
    from ..consensus.poh import PoHConsensus
    from ..core.region_manager import RegionManager
    
    # Create components for region 1
    poh_generator1 = PoHGenerator(target_hash_rate=10000)
    poh_consensus1 = PoHConsensus(
        node_id="node1",
        region="region1",
        poh_generator=poh_generator1
    )
    region_manager1 = RegionManager(
        node_id="node1",
        primary_region="region1"
    )
    
    # Create components for region 2
    poh_generator2 = PoHGenerator(target_hash_rate=10000)
    poh_consensus2 = PoHConsensus(
        node_id="node2",
        region="region2",
        poh_generator=poh_generator2
    )
    region_manager2 = RegionManager(
        node_id="node2",
        primary_region="region2"
    )
    
    # Connect the regions
    region_manager1.create_region("region2", "Region 2")
    region_manager2.create_region("region1", "Region 1")
    region_manager1.connect_regions("region1", "region2")
    region_manager2.connect_regions("region2", "region1")
    
    # Create region sync for both regions
    region_sync1 = RegionSync(
        region_manager=region_manager1,
        poh_consensus=poh_consensus1,
        sync_interval=0.5
    )
    
    region_sync2 = RegionSync(
        region_manager=region_manager2,
        poh_consensus=poh_consensus2,
        sync_interval=0.5
    )
    
    # Start all components
    poh_consensus1.start()
    poh_consensus2.start()
    region_manager1.start()
    region_manager2.start()
    region_sync1.start()
    region_sync2.start()
    
    try:
        # Run for a while
        print("Running region sync for 10 seconds...")
        for i in range(10):
            time.sleep(1)
            
            # Print status
            status1 = region_sync1.get_status()
            status2 = region_sync2.get_status()
            
            print(f"\nIteration {i+1}:")
            print(f"Region 1 status: {status1['primary_region']}, connected to {status1['connected_regions']}")
            print(f"Region 2 status: {status2['primary_region']}, connected to {status2['connected_regions']}")
            print(f"Region 1 messages: outgoing={status1['outgoing_messages']}, incoming={status1['incoming_messages']}, processed={status1['processed_messages']}")
            print(f"Region 2 messages: outgoing={status2['outgoing_messages']}, incoming={status2['incoming_messages']}, processed={status2['processed_messages']}")
    
    finally:
        # Stop all components
        region_sync1.stop()
        region_sync2.stop()
        region_manager1.stop()
        region_manager2.stop()
        poh_consensus1.stop()
        poh_consensus2.stop()