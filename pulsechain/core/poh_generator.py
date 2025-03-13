#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PulseChain - Proof of History Generator
=======================================

This module implements the Proof of History (PoH) generator for PulseChain.
It creates a verifiable sequence of hashes that proves the passage of time.
The implementation extends Solana's PoH by incorporating environmental data.
"""

import time
import hashlib
import json
import threading
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("poh_generator")

@dataclass
class PoHHash:
    """A single hash in the PoH sequence."""
    hash: bytes
    counter: int
    timestamp: float
    env_data_hash: Optional[bytes] = None
    prev_hash: Optional[bytes] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "hash": self.hash.hex(),
            "counter": self.counter,
            "timestamp": self.timestamp,
            "env_data_hash": self.env_data_hash.hex() if self.env_data_hash else None,
            "prev_hash": self.prev_hash.hex() if self.prev_hash else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PoHHash':
        """Create from dictionary after deserialization."""
        return cls(
            hash=bytes.fromhex(data["hash"]),
            counter=data["counter"],
            timestamp=data["timestamp"],
            env_data_hash=bytes.fromhex(data["env_data_hash"]) if data.get("env_data_hash") else None,
            prev_hash=bytes.fromhex(data["prev_hash"]) if data.get("prev_hash") else None
        )


class PoHGenerator:
    """
    Proof of History generator that creates a verifiable sequence of hashes.
    
    This implementation extends Solana's PoH by incorporating environmental data
    to enhance the randomness and security of the hash chain.
    """
    
    def __init__(self, 
                 initial_hash: Optional[bytes] = None, 
                 counter_start: int = 0,
                 target_hash_rate: int = 1000000):  # Target hashes per second
        """
        Initialize the PoH generator.
        
        Args:
            initial_hash: Optional initial hash to start the sequence
            counter_start: Starting counter value
            target_hash_rate: Target number of hashes per second
        """
        self.last_hash = initial_hash or hashlib.sha256(b"PulseChain PoH Genesis").digest()
        self.counter = counter_start
        self.env_data_hash = hashlib.sha256(b"Initial Environment Data").digest()
        self.target_hash_rate = target_hash_rate
        self.hash_chain: List[PoHHash] = []
        self.lock = threading.Lock()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # Performance tracking
        self.last_performance_check = time.time()
        self.hashes_since_check = 0
        self.current_hash_rate = 0
        
        logger.info(f"PoH Generator initialized with target rate of {target_hash_rate} hashes/sec")
    
    def next(self, env_data: Optional[Union[bytes, Dict, List]] = None) -> PoHHash:
        """
        Generate the next hash in the sequence.
        
        Args:
            env_data: Optional environmental data to incorporate
            
        Returns:
            The newly generated PoH hash
        """
        with self.lock:
            # Update environmental data hash if provided
            if env_data is not None:
                if isinstance(env_data, (dict, list)):
                    env_data = json.dumps(env_data, sort_keys=True).encode()
                self.env_data_hash = hashlib.sha256(env_data).digest()
            
            # Prepare input for hashing
            prev_hash = self.last_hash
            input_data = prev_hash + self.counter.to_bytes(8, 'little') + self.env_data_hash
            
            # Generate new hash
            new_hash = hashlib.sha256(input_data).digest()
            
            # Update state
            self.counter += 1
            self.last_hash = new_hash
            
            # Create PoH hash object
            poh_hash = PoHHash(
                hash=new_hash,
                counter=self.counter,
                timestamp=time.time(),
                env_data_hash=self.env_data_hash,
                prev_hash=prev_hash
            )
            
            # Add to chain
            self.hash_chain.append(poh_hash)
            if len(self.hash_chain) > 1000:  # Limit chain size in memory
                self.hash_chain = self.hash_chain[-1000:]
            
            # Update performance metrics
            self.hashes_since_check += 1
            current_time = time.time()
            elapsed = current_time - self.last_performance_check
            if elapsed >= 1.0:  # Update hash rate every second
                self.current_hash_rate = self.hashes_since_check / elapsed
                self.hashes_since_check = 0
                self.last_performance_check = current_time
            
            return poh_hash
    
    def verify(self, poh_hash: PoHHash) -> bool:
        """
        Verify that a PoH hash is valid.
        
        Args:
            poh_hash: The PoH hash to verify
            
        Returns:
            True if the hash is valid, False otherwise
        """
        if not poh_hash.prev_hash:
            return False
        
        # Reconstruct the input data
        input_data = (poh_hash.prev_hash + 
                     (poh_hash.counter - 1).to_bytes(8, 'little') + 
                     (poh_hash.env_data_hash or b""))
        
        # Compute the hash
        computed_hash = hashlib.sha256(input_data).digest()
        
        # Verify
        return computed_hash == poh_hash.hash
    
    def start(self) -> None:
        """Start the PoH generator in a background thread."""
        if self.running:
            logger.warning("PoH Generator is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("PoH Generator started in background thread")
    
    def stop(self) -> None:
        """Stop the PoH generator."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
        logger.info("PoH Generator stopped")
    
    def _run(self) -> None:
        """Run the PoH generator continuously."""
        target_interval = 1.0 / self.target_hash_rate
        
        while self.running:
            start_time = time.time()
            
            # Generate next hash
            self.next()
            
            # Calculate time to sleep to maintain target hash rate
            elapsed = time.time() - start_time
            sleep_time = max(0, target_interval - elapsed)
            
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def get_latest_hash(self) -> PoHHash:
        """Get the latest hash in the chain."""
        with self.lock:
            if not self.hash_chain:
                # Generate a hash if none exists
                return self.next()
            return self.hash_chain[-1]
    
    def get_hash_at_counter(self, counter: int) -> Optional[PoHHash]:
        """Get the hash at a specific counter value."""
        with self.lock:
            for poh_hash in reversed(self.hash_chain):
                if poh_hash.counter == counter:
                    return poh_hash
            return None
    
    def get_hash_rate(self) -> float:
        """Get the current hash rate."""
        return self.current_hash_rate
    
    def export_chain(self, start_idx: int = 0, count: int = 100) -> List[Dict[str, Any]]:
        """
        Export a portion of the hash chain for external verification.
        
        Args:
            start_idx: Starting index in the chain
            count: Number of hashes to export
            
        Returns:
            List of hash dictionaries
        """
        with self.lock:
            end_idx = min(start_idx + count, len(self.hash_chain))
            return [h.to_dict() for h in self.hash_chain[start_idx:end_idx]]
    
    def import_chain(self, chain_data: List[Dict[str, Any]]) -> bool:
        """
        Import a hash chain from external source.
        
        Args:
            chain_data: List of hash dictionaries
            
        Returns:
            True if import was successful, False otherwise
        """
        if not chain_data:
            return False
        
        try:
            imported_chain = [PoHHash.from_dict(data) for data in chain_data]
            
            # Verify the chain
            for i in range(1, len(imported_chain)):
                if not self.verify(imported_chain[i]):
                    logger.error(f"Verification failed at index {i}")
                    return False
            
            with self.lock:
                # Update state based on the last hash in the imported chain
                last_imported = imported_chain[-1]
                self.last_hash = last_imported.hash
                self.counter = last_imported.counter
                self.env_data_hash = last_imported.env_data_hash or self.env_data_hash
                
                # Replace or extend our chain
                if len(imported_chain) > len(self.hash_chain):
                    self.hash_chain = imported_chain[-1000:]  # Keep last 1000
                else:
                    # Find overlap point and merge
                    overlap_idx = -1
                    for i, existing_hash in enumerate(self.hash_chain):
                        if existing_hash.counter == imported_chain[0].counter:
                            overlap_idx = i
                            break
                    
                    if overlap_idx >= 0:
                        self.hash_chain = (
                            self.hash_chain[:overlap_idx] + 
                            imported_chain
                        )[-1000:]  # Keep last 1000
            
            logger.info(f"Successfully imported {len(imported_chain)} hashes")
            return True
            
        except Exception as e:
            logger.error(f"Error importing chain: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Create a PoH generator
    poh_gen = PoHGenerator(target_hash_rate=10000)  # 10K hashes per second
    
    # Generate some hashes
    print("Generating initial hashes...")
    for _ in range(5):
        poh_hash = poh_gen.next()
        print(f"Hash: {poh_hash.hash.hex()[:16]}..., Counter: {poh_hash.counter}")
    
    # Add environmental data
    env_data = {
        "temperature": 22.5,
        "humidity": 45.2,
        "timestamp": time.time(),
        "market_data": {
            "btc_price": 45000.0,
            "eth_price": 3000.0
        }
    }
    
    print("\nAdding environmental data...")
    poh_hash = poh_gen.next(env_data)
    print(f"Hash with env data: {poh_hash.hash.hex()[:16]}..., Counter: {poh_hash.counter}")
    
    # Start continuous generation
    print("\nStarting continuous generation for 3 seconds...")
    poh_gen.start()
    time.sleep(3)
    poh_gen.stop()
    
    # Get hash rate
    print(f"\nFinal hash rate: {poh_gen.get_hash_rate():.2f} hashes/sec")
    print(f"Total hashes generated: {len(poh_gen.hash_chain)}")
    
    # Export and verify
    print("\nExporting chain...")
    exported = poh_gen.export_chain(0, 10)
    print(f"Exported {len(exported)} hashes")
    
    # Verify a hash
    latest = poh_gen.get_latest_hash()
    is_valid = poh_gen.verify(latest)
    print(f"\nLatest hash verification: {'Valid' if is_valid else 'Invalid'}")