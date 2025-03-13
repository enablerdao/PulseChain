#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PulseChain - Proof of History Consensus
======================================

This module implements the Proof of History (PoH) consensus mechanism for PulseChain.
It builds on Solana's PoH concept but extends it with environmental data integration.
"""

import time
import hashlib
import json
import threading
import logging
import random
from typing import Dict, List, Optional, Any, Tuple, Set, Callable
from dataclasses import dataclass, field

from ..core.poh_generator import PoHGenerator, PoHHash

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("poh_consensus")

@dataclass
class PoHLeader:
    """Information about a PoH leader."""
    node_id: str
    public_key: bytes
    region: str
    stake: float
    performance_score: float = 1.0
    last_leader_slot: int = 0
    consecutive_slots: int = 0


@dataclass
class PoHSlot:
    """A slot in the PoH timeline."""
    slot_number: int
    start_counter: int
    end_counter: int
    leader_id: str
    start_time: float
    end_time: Optional[float] = None
    hashes: List[PoHHash] = field(default_factory=list)
    confirmations: Set[str] = field(default_factory=set)
    is_finalized: bool = False


class PoHConsensus:
    """
    Proof of History consensus mechanism for PulseChain.
    
    This class manages the PoH timeline, leader selection, and consensus process.
    It integrates environmental data to enhance the security and efficiency of the consensus.
    """
    
    def __init__(self, 
                 node_id: str,
                 region: str,
                 poh_generator: Optional[PoHGenerator] = None,
                 slot_duration: float = 0.4,  # 400ms slots
                 target_hashes_per_slot: int = 10000):
        """
        Initialize the PoH consensus mechanism.
        
        Args:
            node_id: Identifier for this node
            region: Geographic region of this node
            poh_generator: Optional existing PoH generator
            slot_duration: Duration of each slot in seconds
            target_hashes_per_slot: Target number of hashes per slot
        """
        self.node_id = node_id
        self.region = region
        self.poh_generator = poh_generator or PoHGenerator(
            target_hash_rate=int(target_hashes_per_slot / slot_duration)
        )
        self.slot_duration = slot_duration
        self.target_hashes_per_slot = target_hashes_per_slot
        
        # Slots and timeline
        self.current_slot_number = 0
        self.slots: Dict[int, PoHSlot] = {}
        self.finalized_slots: List[int] = []
        
        # Leaders
        self.leaders: Dict[str, PoHLeader] = {}
        self.current_leader_id: Optional[str] = None
        self.is_leader = False
        
        # Validators
        self.validators: Set[str] = set()
        
        # Callbacks
        self.on_new_slot_callbacks: List[Callable[[PoHSlot], None]] = []
        self.on_slot_finalized_callbacks: List[Callable[[PoHSlot], None]] = []
        
        # Threading
        self.lock = threading.Lock()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        logger.info(f"PoH Consensus initialized for node {node_id} in region {region}")
    
    def register_leader(self, 
                       node_id: str, 
                       public_key: bytes, 
                       region: str, 
                       stake: float) -> None:
        """
        Register a node as a potential leader.
        
        Args:
            node_id: Identifier for the node
            public_key: Public key of the node
            region: Geographic region of the node
            stake: Stake amount of the node
        """
        with self.lock:
            self.leaders[node_id] = PoHLeader(
                node_id=node_id,
                public_key=public_key,
                region=region,
                stake=stake
            )
            logger.info(f"Registered leader {node_id} from region {region} with stake {stake}")
    
    def register_validator(self, node_id: str) -> None:
        """
        Register a node as a validator.
        
        Args:
            node_id: Identifier for the node
        """
        with self.lock:
            self.validators.add(node_id)
            logger.info(f"Registered validator {node_id}")
    
    def select_leader(self, slot_number: int) -> str:
        """
        Select a leader for the given slot number.
        
        Args:
            slot_number: The slot number to select a leader for
            
        Returns:
            The node ID of the selected leader
        """
        with self.lock:
            if not self.leaders:
                # If no leaders registered, use self
                return self.node_id
            
            # Get the latest PoH hash as a source of randomness
            latest_hash = self.poh_generator.get_latest_hash()
            
            # Create a deterministic seed based on slot number and latest hash
            seed = int.from_bytes(
                hashlib.sha256(
                    latest_hash.hash + slot_number.to_bytes(8, 'little')
                ).digest()[:8], 
                'little'
            )
            
            # Set random seed for deterministic selection
            random.seed(seed)
            
            # Calculate selection weights based on stake and performance
            total_weight = sum(
                leader.stake * leader.performance_score 
                for leader in self.leaders.values()
            )
            
            if total_weight == 0:
                # If all weights are zero, select randomly
                return random.choice(list(self.leaders.keys()))
            
            # Select leader based on weighted probability
            selection_point = random.uniform(0, total_weight)
            cumulative_weight = 0
            
            for node_id, leader in self.leaders.items():
                weight = leader.stake * leader.performance_score
                cumulative_weight += weight
                
                if cumulative_weight >= selection_point:
                    # Update leader stats
                    leader.last_leader_slot = slot_number
                    
                    # Check for consecutive slots
                    if self.current_leader_id == node_id:
                        leader.consecutive_slots += 1
                        # Reduce performance score slightly for consecutive slots
                        # to encourage rotation
                        if leader.consecutive_slots > 3:
                            leader.performance_score *= 0.95
                    else:
                        leader.consecutive_slots = 1
                    
                    logger.info(f"Selected leader {node_id} for slot {slot_number}")
                    return node_id
            
            # Fallback (should not reach here)
            return list(self.leaders.keys())[0]
    
    def create_new_slot(self) -> PoHSlot:
        """
        Create a new slot in the PoH timeline.
        
        Returns:
            The newly created slot
        """
        with self.lock:
            self.current_slot_number += 1
            slot_number = self.current_slot_number
            
            # Select leader for this slot
            leader_id = self.select_leader(slot_number)
            self.current_leader_id = leader_id
            self.is_leader = (leader_id == self.node_id)
            
            # Get current PoH state
            latest_hash = self.poh_generator.get_latest_hash()
            start_counter = latest_hash.counter
            
            # Create the slot
            slot = PoHSlot(
                slot_number=slot_number,
                start_counter=start_counter,
                end_counter=start_counter,  # Will be updated at end of slot
                leader_id=leader_id,
                start_time=time.time()
            )
            
            self.slots[slot_number] = slot
            
            # Notify callbacks
            for callback in self.on_new_slot_callbacks:
                try:
                    callback(slot)
                except Exception as e:
                    logger.error(f"Error in new slot callback: {e}")
            
            logger.info(f"Created new slot {slot_number} with leader {leader_id}")
            return slot
    
    def finalize_slot(self, slot_number: int) -> bool:
        """
        Finalize a slot after it has received sufficient confirmations.
        
        Args:
            slot_number: The slot number to finalize
            
        Returns:
            True if the slot was finalized, False otherwise
        """
        with self.lock:
            if slot_number not in self.slots:
                logger.warning(f"Cannot finalize non-existent slot {slot_number}")
                return False
            
            slot = self.slots[slot_number]
            
            if slot.is_finalized:
                return True
            
            # Check if we have enough confirmations (2/3 of validators)
            required_confirmations = max(1, len(self.validators) * 2 // 3)
            if len(slot.confirmations) < required_confirmations:
                logger.debug(
                    f"Slot {slot_number} has {len(slot.confirmations)} confirmations, "
                    f"need {required_confirmations}"
                )
                return False
            
            # Finalize the slot
            slot.is_finalized = True
            slot.end_time = time.time()
            
            # Get the latest PoH state
            latest_hash = self.poh_generator.get_latest_hash()
            slot.end_counter = latest_hash.counter
            
            # Add to finalized slots
            self.finalized_slots.append(slot_number)
            
            # Update leader performance based on slot quality
            if slot.leader_id in self.leaders:
                leader = self.leaders[slot.leader_id]
                
                # Calculate hashes produced in this slot
                hashes_produced = slot.end_counter - slot.start_counter
                hash_ratio = hashes_produced / self.target_hashes_per_slot
                
                # Update performance score (bounded between 0.5 and 1.5)
                if 0.8 <= hash_ratio <= 1.2:
                    # Good performance - within 20% of target
                    leader.performance_score = min(1.5, leader.performance_score * 1.05)
                else:
                    # Poor performance - too few or too many hashes
                    leader.performance_score = max(0.5, leader.performance_score * 0.95)
            
            # Notify callbacks
            for callback in self.on_slot_finalized_callbacks:
                try:
                    callback(slot)
                except Exception as e:
                    logger.error(f"Error in slot finalized callback: {e}")
            
            logger.info(
                f"Finalized slot {slot_number} with {len(slot.confirmations)} confirmations, "
                f"{slot.end_counter - slot.start_counter} hashes"
            )
            return True
    
    def confirm_slot(self, slot_number: int, validator_id: str) -> bool:
        """
        Record a confirmation for a slot from a validator.
        
        Args:
            slot_number: The slot number to confirm
            validator_id: The ID of the validator confirming the slot
            
        Returns:
            True if the confirmation was recorded, False otherwise
        """
        with self.lock:
            if slot_number not in self.slots:
                logger.warning(f"Cannot confirm non-existent slot {slot_number}")
                return False
            
            slot = self.slots[slot_number]
            
            if slot.is_finalized:
                logger.debug(f"Slot {slot_number} is already finalized")
                return True
            
            # Add confirmation
            slot.confirmations.add(validator_id)
            logger.debug(f"Validator {validator_id} confirmed slot {slot_number}")
            
            # Try to finalize the slot
            return self.finalize_slot(slot_number)
    
    def get_slot(self, slot_number: int) -> Optional[PoHSlot]:
        """
        Get a slot by its number.
        
        Args:
            slot_number: The slot number to get
            
        Returns:
            The slot, or None if it doesn't exist
        """
        with self.lock:
            return self.slots.get(slot_number)
    
    def get_current_slot(self) -> Optional[PoHSlot]:
        """
        Get the current slot.
        
        Returns:
            The current slot, or None if no slots exist
        """
        with self.lock:
            return self.slots.get(self.current_slot_number)
    
    def get_latest_finalized_slot(self) -> Optional[PoHSlot]:
        """
        Get the latest finalized slot.
        
        Returns:
            The latest finalized slot, or None if no slots are finalized
        """
        with self.lock:
            if not self.finalized_slots:
                return None
            return self.slots.get(self.finalized_slots[-1])
    
    def on_new_slot(self, callback: Callable[[PoHSlot], None]) -> None:
        """
        Register a callback to be called when a new slot is created.
        
        Args:
            callback: The callback function
        """
        self.on_new_slot_callbacks.append(callback)
    
    def on_slot_finalized(self, callback: Callable[[PoHSlot], None]) -> None:
        """
        Register a callback to be called when a slot is finalized.
        
        Args:
            callback: The callback function
        """
        self.on_slot_finalized_callbacks.append(callback)
    
    def start(self) -> None:
        """Start the PoH consensus mechanism."""
        if self.running:
            logger.warning("PoH Consensus is already running")
            return
        
        # Start the PoH generator if it's not already running
        if not self.poh_generator.running:
            self.poh_generator.start()
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("PoH Consensus started")
    
    def stop(self) -> None:
        """Stop the PoH consensus mechanism."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
        
        # Stop the PoH generator if we started it
        if self.poh_generator.running:
            self.poh_generator.stop()
        
        logger.info("PoH Consensus stopped")
    
    def _run(self) -> None:
        """Run the PoH consensus mechanism."""
        # Create initial slot
        self.create_new_slot()
        last_slot_time = time.time()
        
        while self.running:
            current_time = time.time()
            
            # Check if it's time for a new slot
            if current_time - last_slot_time >= self.slot_duration:
                self.create_new_slot()
                last_slot_time = current_time
            
            # Sleep a bit to avoid busy waiting
            time.sleep(0.01)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the PoH consensus.
        
        Returns:
            A dictionary with status information
        """
        with self.lock:
            return {
                "node_id": self.node_id,
                "region": self.region,
                "current_slot": self.current_slot_number,
                "is_leader": self.is_leader,
                "current_leader": self.current_leader_id,
                "finalized_slots": len(self.finalized_slots),
                "total_slots": len(self.slots),
                "validators": len(self.validators),
                "leaders": len(self.leaders),
                "poh_hash_rate": self.poh_generator.get_hash_rate(),
                "slot_duration": self.slot_duration
            }


# Example usage
if __name__ == "__main__":
    # Create a PoH consensus instance
    poh_consensus = PoHConsensus(
        node_id="node1",
        region="us-west",
        slot_duration=0.5  # 500ms slots
    )
    
    # Register some leaders
    poh_consensus.register_leader(
        node_id="node1",
        public_key=b"node1_pubkey",
        region="us-west",
        stake=100.0
    )
    
    poh_consensus.register_leader(
        node_id="node2",
        public_key=b"node2_pubkey",
        region="us-east",
        stake=150.0
    )
    
    # Register some validators
    for i in range(1, 6):
        poh_consensus.register_validator(f"validator{i}")
    
    # Define callbacks
    def on_new_slot(slot: PoHSlot):
        print(f"New slot created: {slot.slot_number}, leader: {slot.leader_id}")
    
    def on_slot_finalized(slot: PoHSlot):
        print(f"Slot finalized: {slot.slot_number}, confirmations: {len(slot.confirmations)}")
    
    poh_consensus.on_new_slot(on_new_slot)
    poh_consensus.on_slot_finalized(on_slot_finalized)
    
    # Start consensus
    poh_consensus.start()
    
    # Simulate some confirmations
    try:
        for _ in range(10):  # Run for 10 slots
            time.sleep(0.6)  # Wait for a slot to be created
            
            # Get current slot
            current_slot = poh_consensus.get_current_slot()
            if current_slot:
                # Simulate validators confirming the slot
                for i in range(1, 6):
                    poh_consensus.confirm_slot(current_slot.slot_number, f"validator{i}")
    
    finally:
        # Stop consensus
        poh_consensus.stop()
        
        # Print final status
        status = poh_consensus.get_status()
        print("\nFinal status:")
        for key, value in status.items():
            print(f"  {key}: {value}")