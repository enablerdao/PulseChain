#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PulseChain - PoH Consensus Tests
===============================

This module contains tests for the PulseChain PoH consensus mechanism.
"""

import os
import sys
import time
import unittest
import threading
from typing import Dict, List, Optional, Any

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pulsechain.core.poh_generator import PoHGenerator
from pulsechain.consensus.poh import PoHConsensus


class TestPoHGenerator(unittest.TestCase):
    """Tests for the PoH Generator."""
    
    def setUp(self):
        """Set up the test environment."""
        self.poh_generator = PoHGenerator(target_hash_rate=10000)
    
    def tearDown(self):
        """Clean up after the test."""
        if self.poh_generator.running:
            self.poh_generator.stop()
    
    def test_next_hash(self):
        """Test generating the next hash."""
        # Generate a hash
        poh_hash = self.poh_generator.next()
        
        # Check that it has the expected properties
        self.assertIsNotNone(poh_hash.hash)
        self.assertEqual(poh_hash.counter, 1)
        self.assertIsNotNone(poh_hash.timestamp)
        self.assertIsNotNone(poh_hash.env_data_hash)
        
        # Generate another hash
        poh_hash2 = self.poh_generator.next()
        
        # Check that it's different from the first
        self.assertNotEqual(poh_hash.hash, poh_hash2.hash)
        self.assertEqual(poh_hash2.counter, 2)
    
    def test_env_data_integration(self):
        """Test integrating environmental data."""
        # Generate a hash with environmental data
        env_data = {"test": "data", "value": 123}
        poh_hash = self.poh_generator.next(env_data)
        
        # Check that the hash includes the environmental data
        self.assertIsNotNone(poh_hash.env_data_hash)
        
        # Generate another hash with different environmental data
        env_data2 = {"test": "data2", "value": 456}
        poh_hash2 = self.poh_generator.next(env_data2)
        
        # Check that the environmental data hash is different
        self.assertNotEqual(poh_hash.env_data_hash, poh_hash2.env_data_hash)
    
    def test_verification(self):
        """Test hash verification."""
        # Generate a hash
        poh_hash = self.poh_generator.next()
        
        # Verify it
        self.assertTrue(self.poh_generator.verify(poh_hash))
        
        # Modify the hash and verify it fails
        poh_hash.hash = b"invalid_hash"
        self.assertFalse(self.poh_generator.verify(poh_hash))
    
    def test_continuous_generation(self):
        """Test continuous hash generation."""
        # Start continuous generation
        self.poh_generator.start()
        
        # Wait for some hashes to be generated
        time.sleep(0.5)
        
        # Check that hashes were generated
        self.assertGreater(len(self.poh_generator.hash_chain), 0)
        
        # Check the hash rate
        hash_rate = self.poh_generator.get_hash_rate()
        self.assertGreater(hash_rate, 0)
        
        # Stop generation
        self.poh_generator.stop()


class TestPoHConsensus(unittest.TestCase):
    """Tests for the PoH Consensus mechanism."""
    
    def setUp(self):
        """Set up the test environment."""
        self.poh_generator = PoHGenerator(target_hash_rate=10000)
        self.poh_consensus = PoHConsensus(
            node_id="test_node",
            region="test_region",
            poh_generator=self.poh_generator,
            slot_duration=0.1  # 100ms slots for faster testing
        )
    
    def tearDown(self):
        """Clean up after the test."""
        if self.poh_consensus.running:
            self.poh_consensus.stop()
        if self.poh_generator.running:
            self.poh_generator.stop()
    
    def test_slot_creation(self):
        """Test creating a new slot."""
        # Create a slot
        slot = self.poh_consensus.create_new_slot()
        
        # Check that it has the expected properties
        self.assertEqual(slot.slot_number, 1)
        self.assertIsNotNone(slot.start_counter)
        self.assertEqual(slot.leader_id, "test_node")  # Default to self
        self.assertIsNotNone(slot.start_time)
        self.assertFalse(slot.is_finalized)
        
        # Create another slot
        slot2 = self.poh_consensus.create_new_slot()
        
        # Check that it's different from the first
        self.assertEqual(slot2.slot_number, 2)
    
    def test_leader_selection(self):
        """Test leader selection."""
        # Register some leaders
        self.poh_consensus.register_leader(
            node_id="leader1",
            public_key=b"leader1_pubkey",
            region="test_region",
            stake=100.0
        )
        
        self.poh_consensus.register_leader(
            node_id="leader2",
            public_key=b"leader2_pubkey",
            region="test_region",
            stake=200.0
        )
        
        # Select a leader
        leader_id = self.poh_consensus.select_leader(1)
        
        # Check that a leader was selected
        self.assertIsNotNone(leader_id)
        self.assertIn(leader_id, ["leader1", "leader2", "test_node"])
    
    def test_slot_confirmation(self):
        """Test confirming a slot."""
        # Create a slot
        slot = self.poh_consensus.create_new_slot()
        
        # Register some validators
        self.poh_consensus.register_validator("validator1")
        self.poh_consensus.register_validator("validator2")
        self.poh_consensus.register_validator("validator3")
        
        # Confirm the slot
        self.poh_consensus.confirm_slot(slot.slot_number, "validator1")
        self.poh_consensus.confirm_slot(slot.slot_number, "validator2")
        
        # Check that the slot has confirmations
        slot = self.poh_consensus.get_slot(slot.slot_number)
        self.assertEqual(len(slot.confirmations), 2)
        
        # Confirm again with the same validator (should be ignored)
        self.poh_consensus.confirm_slot(slot.slot_number, "validator1")
        slot = self.poh_consensus.get_slot(slot.slot_number)
        self.assertEqual(len(slot.confirmations), 2)
        
        # Confirm with a third validator to finalize
        self.poh_consensus.confirm_slot(slot.slot_number, "validator3")
        
        # Check that the slot is finalized
        slot = self.poh_consensus.get_slot(slot.slot_number)
        self.assertTrue(slot.is_finalized)
    
    def test_continuous_operation(self):
        """Test continuous operation."""
        # Register some validators
        self.poh_consensus.register_validator("validator1")
        self.poh_consensus.register_validator("validator2")
        
        # Start consensus
        self.poh_consensus.start()
        
        # Wait for some slots to be created
        time.sleep(0.5)
        
        # Check that slots were created
        self.assertGreater(self.poh_consensus.current_slot_number, 0)
        
        # Confirm some slots
        for i in range(1, self.poh_consensus.current_slot_number + 1):
            self.poh_consensus.confirm_slot(i, "validator1")
            self.poh_consensus.confirm_slot(i, "validator2")
        
        # Check that some slots were finalized
        self.assertGreater(len(self.poh_consensus.finalized_slots), 0)
        
        # Stop consensus
        self.poh_consensus.stop()


if __name__ == '__main__':
    unittest.main()