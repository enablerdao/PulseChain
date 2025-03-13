#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PulseChain - Solana Data Source Tests
===================================

This module contains tests for the Solana data source.
"""

import os
import sys
import time
import unittest
import threading
from typing import Dict, List, Optional, Any
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pulsechain.utils.solana_data_source import SolanaDataSource, SolanaClusterInfo


class MockResponse:
    """Mock response for requests."""
    
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
    
    def json(self):
        return self.json_data


class TestSolanaDataSource(unittest.TestCase):
    """Tests for the Solana Data Source."""
    
    def setUp(self):
        """Set up the test environment."""
        self.solana_source = SolanaDataSource(
            primary_cluster="testnet",
            update_interval=1.0
        )
    
    def tearDown(self):
        """Clean up after the test."""
        if self.solana_source.running:
            self.solana_source.stop()
    
    @patch('pulsechain.utils.solana_data_source.requests.post')
    def test_get_slot(self, mock_post):
        """Test getting the current slot."""
        # Mock the response
        mock_post.return_value = MockResponse({
            "jsonrpc": "2.0",
            "result": 12345,
            "id": 1
        })
        
        # Get the slot
        slot = self.solana_source.get_slot()
        
        # Check that the slot is correct
        self.assertEqual(slot, 12345)
        
        # Check that the request was made correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['method'], 'getSlot')
    
    @patch('pulsechain.utils.solana_data_source.requests.post')
    def test_get_block_time(self, mock_post):
        """Test getting the block time."""
        # Mock the response
        mock_post.return_value = MockResponse({
            "jsonrpc": "2.0",
            "result": 1625097600,
            "id": 1
        })
        
        # Get the block time
        block_time = self.solana_source.get_block_time(12345)
        
        # Check that the block time is correct
        self.assertEqual(block_time, 1625097600)
        
        # Check that the request was made correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['method'], 'getBlockTime')
        self.assertEqual(kwargs['json']['params'], [12345])
    
    @patch('pulsechain.utils.solana_data_source.requests.post')
    def test_get_health(self, mock_post):
        """Test getting the health."""
        # Mock the response
        mock_post.return_value = MockResponse({
            "jsonrpc": "2.0",
            "result": "ok",
            "id": 1
        })
        
        # Get the health
        health = self.solana_source.get_health()
        
        # Check that the health is correct
        self.assertTrue(health)
        
        # Check that the request was made correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['method'], 'getHealth')
    
    @patch('pulsechain.utils.solana_data_source.requests.post')
    def test_get_version(self, mock_post):
        """Test getting the version."""
        # Mock the response
        mock_post.return_value = MockResponse({
            "jsonrpc": "2.0",
            "result": {
                "solana-core": "1.7.0"
            },
            "id": 1
        })
        
        # Get the version
        version = self.solana_source.get_version()
        
        # Check that the version is correct
        self.assertEqual(version, {"solana-core": "1.7.0"})
        
        # Check that the request was made correctly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['method'], 'getVersion')
    
    @patch('pulsechain.utils.solana_data_source.requests.post')
    def test_collect_data(self, mock_post):
        """Test collecting data."""
        # Mock the responses
        mock_post.side_effect = [
            # getSlot
            MockResponse({
                "jsonrpc": "2.0",
                "result": 12345,
                "id": 1
            }),
            # getBlockTime
            MockResponse({
                "jsonrpc": "2.0",
                "result": 1625097600,
                "id": 1
            }),
            # getRecentPerformanceSamples
            MockResponse({
                "jsonrpc": "2.0",
                "result": [
                    {
                        "numSlots": 60,
                        "numTransactions": 1000,
                        "samplePeriodSecs": 60
                    }
                ],
                "id": 1
            }),
            # getHealth
            MockResponse({
                "jsonrpc": "2.0",
                "result": "ok",
                "id": 1
            }),
            # getVersion
            MockResponse({
                "jsonrpc": "2.0",
                "result": {
                    "solana-core": "1.7.0"
                },
                "id": 1
            })
        ]
        
        # Collect data
        data = self.solana_source.collect_data()
        
        # Check that the data is correct
        self.assertEqual(data["slot"], 12345)
        self.assertEqual(data["block_time"], 1625097600)
        self.assertEqual(data["performance"][0]["numSlots"], 60)
        self.assertEqual(data["performance"][0]["numTransactions"], 1000)
        self.assertTrue(data["health"])
        self.assertEqual(data["version"]["solana-core"], "1.7.0")
        
        # Check that the requests were made correctly
        self.assertEqual(mock_post.call_count, 5)
    
    def test_add_custom_cluster(self):
        """Test adding a custom cluster."""
        # Add a custom cluster
        result = self.solana_source.add_custom_cluster(
            cluster_id="custom",
            name="Custom Cluster",
            rpc_url="https://custom.solana.com"
        )
        
        # Check that the cluster was added
        self.assertTrue(result)
        self.assertIn("custom", self.solana_source.clusters)
        self.assertEqual(self.solana_source.clusters["custom"].name, "Custom Cluster")
        self.assertEqual(self.solana_source.clusters["custom"].rpc_url, "https://custom.solana.com")
    
    def test_set_primary_cluster(self):
        """Test setting the primary cluster."""
        # Set the primary cluster
        result = self.solana_source.set_primary_cluster("mainnet-beta")
        
        # Check that the primary cluster was set
        self.assertTrue(result)
        self.assertEqual(self.solana_source.primary_cluster, "mainnet-beta")
    
    def test_on_data_updated(self):
        """Test the data updated callback."""
        # Create a mock callback
        callback = MagicMock()
        
        # Register the callback
        self.solana_source.on_data_updated(callback)
        
        # Simulate data collection
        with patch.object(self.solana_source, 'get_slot', return_value=12345), \
             patch.object(self.solana_source, 'get_block_time', return_value=1625097600), \
             patch.object(self.solana_source, 'get_recent_performance', return_value=[]), \
             patch.object(self.solana_source, 'get_health', return_value=True), \
             patch.object(self.solana_source, 'get_version', return_value={"solana-core": "1.7.0"}):
            
            # Collect data
            self.solana_source.collect_data()
        
        # Check that the callback was called
        callback.assert_called_once()
        args, kwargs = callback.call_args
        self.assertEqual(args[0]["slot"], 12345)
        self.assertEqual(args[0]["block_time"], 1625097600)
        self.assertTrue(args[0]["health"])
        self.assertEqual(args[0]["version"]["solana-core"], "1.7.0")


if __name__ == '__main__':
    unittest.main()