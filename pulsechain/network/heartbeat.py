#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PulseChain - Heartbeat Protocol
==============================

This module implements the Heartbeat protocol for PulseChain.
It provides real-time node status monitoring and time synchronization verification.
"""

import time
import hashlib
import json
import threading
import logging
import socket
import struct
import random
from typing import Dict, List, Optional, Any, Tuple, Set, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

from ..consensus.poh import PoHConsensus, PoHSlot, PoHHash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("heartbeat")

try:
    import ed25519
    HAVE_ED25519 = True
except ImportError:
    logger.warning("ed25519 module not found, using simulated signatures")
    HAVE_ED25519 = False


@dataclass
class HeartbeatMessage:
    """A heartbeat message sent between nodes."""
    node_id: str
    poh_slot: int
    poh_hash: bytes
    sequence: int
    timestamp: float
    region: str
    signature: Optional[bytes] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "node_id": self.node_id,
            "poh_slot": self.poh_slot,
            "poh_hash": self.poh_hash.hex(),
            "sequence": self.sequence,
            "timestamp": self.timestamp,
            "region": self.region,
            "signature": self.signature.hex() if self.signature else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HeartbeatMessage':
        """Create from dictionary after deserialization."""
        return cls(
            node_id=data["node_id"],
            poh_slot=data["poh_slot"],
            poh_hash=bytes.fromhex(data["poh_hash"]),
            sequence=data["sequence"],
            timestamp=data["timestamp"],
            region=data["region"],
            signature=bytes.fromhex(data["signature"]) if data.get("signature") else None
        )
    
    def sign(self, private_key: bytes) -> None:
        """
        Sign the heartbeat message.
        
        Args:
            private_key: Ed25519 private key
        """
        if not HAVE_ED25519:
            # Simulate signature if ed25519 module is not available
            message = self._get_message_bytes()
            self.signature = hashlib.sha256(private_key + message).digest()
            return
        
        # Create signing key
        signing_key = ed25519.SigningKey(private_key)
        
        # Sign the message
        message = self._get_message_bytes()
        self.signature = signing_key.sign(message)
    
    def verify(self, public_key: bytes) -> bool:
        """
        Verify the signature of the heartbeat message.
        
        Args:
            public_key: Ed25519 public key
            
        Returns:
            True if the signature is valid, False otherwise
        """
        if not self.signature:
            return False
        
        if not HAVE_ED25519:
            # Always return True for simulated signatures
            return True
        
        try:
            # Create verifying key
            verifying_key = ed25519.VerifyingKey(public_key)
            
            # Verify the signature
            message = self._get_message_bytes()
            verifying_key.verify(self.signature, message)
            return True
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def _get_message_bytes(self) -> bytes:
        """Get the bytes to sign/verify."""
        return (
            self.node_id.encode() +
            struct.pack("!Q", self.poh_slot) +
            self.poh_hash +
            struct.pack("!Q", self.sequence) +
            struct.pack("!d", self.timestamp) +
            self.region.encode()
        )


@dataclass
class NodeInfo:
    """Information about a node in the network."""
    node_id: str
    public_key: bytes
    region: str
    last_heartbeat: Optional[HeartbeatMessage] = None
    last_seen: float = 0.0
    sequence_seen: Set[int] = field(default_factory=set)
    latency_samples: List[float] = field(default_factory=list)
    avg_latency: float = 0.0
    status: str = "unknown"


class HeartbeatProtocol:
    """
    Heartbeat protocol for PulseChain.
    
    This class implements the heartbeat mechanism that provides real-time
    node status monitoring and time synchronization verification.
    """
    
    def __init__(self, 
                 node_id: str,
                 region: str,
                 poh_consensus: PoHConsensus,
                 private_key: Optional[bytes] = None,
                 public_key: Optional[bytes] = None,
                 heartbeat_interval: float = 0.1,  # 100ms
                 node_timeout: float = 1.0):  # 1 second
        """
        Initialize the heartbeat protocol.
        
        Args:
            node_id: Identifier for this node
            region: Geographic region of this node
            poh_consensus: The PoH consensus mechanism to integrate with
            private_key: Optional Ed25519 private key for signing
            public_key: Optional Ed25519 public key for verification
            heartbeat_interval: Interval between heartbeats (in seconds)
            node_timeout: Time after which a node is considered offline (in seconds)
        """
        self.node_id = node_id
        self.region = region
        self.poh_consensus = poh_consensus
        
        # Generate keys if not provided
        if not private_key or not public_key:
            if HAVE_ED25519:
                signing_key = ed25519.SigningKey.generate()
                private_key = signing_key.to_bytes()
                public_key = signing_key.get_verifying_key().to_bytes()
            else:
                # Generate simulated keys
                seed = hashlib.sha256(f"{node_id}:{time.time()}".encode()).digest()
                private_key = seed
                public_key = hashlib.sha256(seed).digest()
        
        self.private_key = private_key
        self.public_key = public_key
        
        # Heartbeat settings
        self.heartbeat_interval = heartbeat_interval
        self.node_timeout = node_timeout
        self.sequence = 0
        
        # Node registry
        self.nodes: Dict[str, NodeInfo] = {}
        
        # Received heartbeats
        self.received_heartbeats: List[HeartbeatMessage] = []
        
        # Callbacks
        self.on_heartbeat_callbacks: List[Callable[[HeartbeatMessage], None]] = []
        self.on_node_status_change_callbacks: List[Callable[[str, str], None]] = []
        
        # Threading
        self.lock = threading.Lock()
        self.running = False
        self.send_thread: Optional[threading.Thread] = None
        self.process_thread: Optional[threading.Thread] = None
        
        # Register ourselves
        self.register_node(node_id, public_key, region)
        
        logger.info(f"Heartbeat Protocol initialized for node {node_id} in region {region}")
    
    def register_node(self, 
                     node_id: str, 
                     public_key: bytes, 
                     region: str) -> None:
        """
        Register a node in the network.
        
        Args:
            node_id: Identifier for the node
            public_key: Ed25519 public key of the node
            region: Geographic region of the node
        """
        with self.lock:
            self.nodes[node_id] = NodeInfo(
                node_id=node_id,
                public_key=public_key,
                region=region,
                last_seen=time.time(),
                status="active" if node_id == self.node_id else "unknown"
            )
            logger.info(f"Registered node {node_id} from region {region}")
    
    def create_heartbeat(self) -> HeartbeatMessage:
        """
        Create a new heartbeat message.
        
        Returns:
            The created heartbeat message
        """
        with self.lock:
            # Get current PoH state
            current_slot = self.poh_consensus.get_current_slot()
            if not current_slot:
                # If no slot exists yet, use defaults
                slot_number = 0
                poh_hash = hashlib.sha256(b"PulseChain Genesis").digest()
            else:
                slot_number = current_slot.slot_number
                # Get the latest hash from the PoH generator
                latest_hash = self.poh_consensus.poh_generator.get_latest_hash()
                poh_hash = latest_hash.hash
            
            # Increment sequence number
            self.sequence += 1
            
            # Create heartbeat
            heartbeat = HeartbeatMessage(
                node_id=self.node_id,
                poh_slot=slot_number,
                poh_hash=poh_hash,
                sequence=self.sequence,
                timestamp=time.time(),
                region=self.region
            )
            
            # Sign the heartbeat
            heartbeat.sign(self.private_key)
            
            return heartbeat
    
    def process_heartbeat(self, heartbeat: HeartbeatMessage) -> bool:
        """
        Process a received heartbeat message.
        
        Args:
            heartbeat: The heartbeat message to process
            
        Returns:
            True if the heartbeat was processed successfully, False otherwise
        """
        with self.lock:
            # Check if we know this node
            if heartbeat.node_id not in self.nodes:
                logger.warning(f"Received heartbeat from unknown node: {heartbeat.node_id}")
                return False
            
            node = self.nodes[heartbeat.node_id]
            
            # Verify signature
            if not heartbeat.verify(node.public_key):
                logger.warning(f"Invalid signature on heartbeat from {heartbeat.node_id}")
                return False
            
            # Check for replay attacks
            if heartbeat.sequence in node.sequence_seen:
                logger.warning(f"Duplicate sequence number {heartbeat.sequence} from {heartbeat.node_id}")
                return False
            
            # Check for future timestamps
            current_time = time.time()
            if heartbeat.timestamp > current_time + 1.0:  # Allow 1 second clock skew
                logger.warning(f"Future timestamp on heartbeat from {heartbeat.node_id}")
                return False
            
            # Update node info
            old_status = node.status
            node.last_heartbeat = heartbeat
            node.last_seen = current_time
            node.sequence_seen.add(heartbeat.sequence)
            
            # Limit the size of sequence_seen set
            if len(node.sequence_seen) > 1000:
                node.sequence_seen = set(sorted(node.sequence_seen)[-1000:])
            
            # Calculate latency
            latency = current_time - heartbeat.timestamp
            node.latency_samples.append(latency)
            
            # Limit the number of latency samples
            if len(node.latency_samples) > 100:
                node.latency_samples = node.latency_samples[-100:]
            
            # Update average latency
            node.avg_latency = sum(node.latency_samples) / len(node.latency_samples)
            
            # Update status
            node.status = "active"
            
            # Add to received heartbeats
            self.received_heartbeats.append(heartbeat)
            
            # Limit the number of stored heartbeats
            if len(self.received_heartbeats) > 1000:
                self.received_heartbeats = self.received_heartbeats[-1000:]
            
            # Notify callbacks
            for callback in self.on_heartbeat_callbacks:
                try:
                    callback(heartbeat)
                except Exception as e:
                    logger.error(f"Error in heartbeat callback: {e}")
            
            # Notify status change callbacks
            if old_status != node.status:
                for callback in self.on_node_status_change_callbacks:
                    try:
                        callback(heartbeat.node_id, node.status)
                    except Exception as e:
                        logger.error(f"Error in status change callback: {e}")
            
            return True
    
    def check_node_timeouts(self) -> None:
        """Check for nodes that have timed out."""
        with self.lock:
            current_time = time.time()
            
            for node_id, node in self.nodes.items():
                # Skip ourselves
                if node_id == self.node_id:
                    continue
                
                # Check if node has timed out
                if node.status == "active" and current_time - node.last_seen > self.node_timeout:
                    old_status = node.status
                    node.status = "timeout"
                    
                    # Notify status change callbacks
                    for callback in self.on_node_status_change_callbacks:
                        try:
                            callback(node_id, node.status)
                        except Exception as e:
                            logger.error(f"Error in status change callback: {e}")
                    
                    logger.info(f"Node {node_id} timed out after {current_time - node.last_seen:.2f}s")
    
    def on_heartbeat(self, callback: Callable[[HeartbeatMessage], None]) -> None:
        """
        Register a callback to be called when a heartbeat is received.
        
        Args:
            callback: The callback function
        """
        self.on_heartbeat_callbacks.append(callback)
    
    def on_node_status_change(self, callback: Callable[[str, str], None]) -> None:
        """
        Register a callback to be called when a node's status changes.
        
        Args:
            callback: The callback function (node_id, new_status)
        """
        self.on_node_status_change_callbacks.append(callback)
    
    def start(self) -> None:
        """Start the heartbeat protocol."""
        if self.running:
            logger.warning("Heartbeat Protocol is already running")
            return
        
        self.running = True
        self.send_thread = threading.Thread(target=self._send_heartbeats, daemon=True)
        self.process_thread = threading.Thread(target=self._process_timeouts, daemon=True)
        
        self.send_thread.start()
        self.process_thread.start()
        
        logger.info("Heartbeat Protocol started")
    
    def stop(self) -> None:
        """Stop the heartbeat protocol."""
        self.running = False
        
        if self.send_thread:
            self.send_thread.join(timeout=2.0)
            self.send_thread = None
        
        if self.process_thread:
            self.process_thread.join(timeout=2.0)
            self.process_thread = None
        
        logger.info("Heartbeat Protocol stopped")
    
    def _send_heartbeats(self) -> None:
        """Send heartbeats periodically."""
        while self.running:
            try:
                # Create and "send" heartbeat
                heartbeat = self.create_heartbeat()
                
                # In a real implementation, this would send the heartbeat to other nodes
                # For now, we just process it locally
                self.process_heartbeat(heartbeat)
                
                # Log occasionally
                if self.sequence % 100 == 0:
                    logger.debug(f"Sent heartbeat {self.sequence}")
                
            except Exception as e:
                logger.error(f"Error sending heartbeat: {e}")
            
            # Sleep until next heartbeat
            time.sleep(self.heartbeat_interval)
    
    def _process_timeouts(self) -> None:
        """Check for node timeouts periodically."""
        while self.running:
            try:
                self.check_node_timeouts()
            except Exception as e:
                logger.error(f"Error checking node timeouts: {e}")
            
            # Sleep for a bit
            time.sleep(self.node_timeout / 2)
    
    def get_node_status(self, node_id: str) -> Optional[str]:
        """
        Get the status of a node.
        
        Args:
            node_id: The ID of the node
            
        Returns:
            The node's status, or None if the node is not known
        """
        with self.lock:
            if node_id in self.nodes:
                return self.nodes[node_id].status
            return None
    
    def get_active_nodes(self) -> List[str]:
        """
        Get a list of active nodes.
        
        Returns:
            List of active node IDs
        """
        with self.lock:
            return [
                node_id for node_id, node in self.nodes.items()
                if node.status == "active"
            ]
    
    def get_region_nodes(self, region: str) -> List[str]:
        """
        Get a list of nodes in a specific region.
        
        Args:
            region: The region to get nodes for
            
        Returns:
            List of node IDs in the region
        """
        with self.lock:
            return [
                node_id for node_id, node in self.nodes.items()
                if node.region == region
            ]
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the heartbeat protocol.
        
        Returns:
            A dictionary with status information
        """
        with self.lock:
            return {
                "node_id": self.node_id,
                "region": self.region,
                "sequence": self.sequence,
                "heartbeat_interval": self.heartbeat_interval,
                "node_timeout": self.node_timeout,
                "nodes": {
                    node_id: {
                        "status": node.status,
                        "region": node.region,
                        "last_seen": node.last_seen,
                        "avg_latency": node.avg_latency
                    }
                    for node_id, node in self.nodes.items()
                },
                "active_nodes": len(self.get_active_nodes()),
                "received_heartbeats": len(self.received_heartbeats)
            }


# Example usage
if __name__ == "__main__":
    from ..core.poh_generator import PoHGenerator
    from ..consensus.poh import PoHConsensus
    
    # Create a PoH generator and consensus
    poh_generator = PoHGenerator(target_hash_rate=10000)
    poh_consensus = PoHConsensus(
        node_id="node1",
        region="us-west",
        poh_generator=poh_generator
    )
    
    # Create the heartbeat protocol
    heartbeat_protocol = HeartbeatProtocol(
        node_id="node1",
        region="us-west",
        poh_consensus=poh_consensus,
        heartbeat_interval=0.1  # 100ms
    )
    
    # Register some other nodes
    for i in range(2, 6):
        region = f"region{i}"
        node_id = f"node{i}"
        
        # Generate a simulated public key
        if HAVE_ED25519:
            public_key = ed25519.SigningKey.generate().get_verifying_key().to_bytes()
        else:
            seed = hashlib.sha256(f"{node_id}:{time.time()}".encode()).digest()
            public_key = hashlib.sha256(seed).digest()
        
        heartbeat_protocol.register_node(node_id, public_key, region)
    
    # Define callbacks
    def on_heartbeat(heartbeat: HeartbeatMessage):
        print(f"Received heartbeat from {heartbeat.node_id} in slot {heartbeat.poh_slot}")
    
    def on_status_change(node_id: str, status: str):
        print(f"Node {node_id} status changed to {status}")
    
    heartbeat_protocol.on_heartbeat(on_heartbeat)
    heartbeat_protocol.on_node_status_change(on_status_change)
    
    # Start the components
    poh_consensus.start()
    heartbeat_protocol.start()
    
    try:
        # Simulate some heartbeats from other nodes
        for _ in range(5):
            time.sleep(0.5)
            
            # Create a heartbeat from node2
            heartbeat = HeartbeatMessage(
                node_id="node2",
                poh_slot=poh_consensus.current_slot_number,
                poh_hash=poh_generator.get_latest_hash().hash,
                sequence=random.randint(1, 1000),
                timestamp=time.time(),
                region="region2"
            )
            
            # Sign it with a simulated key
            if HAVE_ED25519:
                signing_key = ed25519.SigningKey.generate()
                heartbeat_protocol.nodes["node2"].public_key = signing_key.get_verifying_key().to_bytes()
                heartbeat.sign(signing_key.to_bytes())
            else:
                seed = hashlib.sha256(b"node2_key").digest()
                heartbeat_protocol.nodes["node2"].public_key = hashlib.sha256(seed).digest()
                heartbeat.signature = hashlib.sha256(seed + heartbeat._get_message_bytes()).digest()
            
            # Process it
            heartbeat_protocol.process_heartbeat(heartbeat)
        
        # Wait for timeouts
        print("\nWaiting for node timeouts...")
        time.sleep(2.0)
        
        # Print final status
        status = heartbeat_protocol.get_status()
        print("\nFinal status:")
        print(f"Active nodes: {status['active_nodes']}")
        for node_id, node_info in status['nodes'].items():
            print(f"  {node_id}: {node_info['status']} (region: {node_info['region']})")
    
    finally:
        # Stop the components
        heartbeat_protocol.stop()
        poh_consensus.stop()