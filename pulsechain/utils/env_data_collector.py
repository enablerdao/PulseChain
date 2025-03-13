#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PulseChain - Environmental Data Collector
=======================================

This module implements the environmental data collection for PulseChain.
It collects data from various sources to be used in the consensus mechanism.
"""

import time
import hashlib
import json
import threading
import logging
import random
import os
import socket
from typing import Dict, List, Optional, Any, Tuple, Set, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("env_data_collector")


class DataSourceType(Enum):
    """Types of environmental data sources."""
    MARKET = "market"
    WEATHER = "weather"
    TIME = "time"
    NETWORK = "network"
    SYSTEM = "system"
    CUSTOM = "custom"


@dataclass
class DataSourceConfig:
    """Configuration for a data source."""
    source_id: str
    source_type: DataSourceType
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    update_interval: float = 60.0  # seconds
    params: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class DataPoint:
    """A single data point collected from a source."""
    source_id: str
    source_type: DataSourceType
    timestamp: float
    data: Dict[str, Any]
    hash: Optional[bytes] = None
    
    def __post_init__(self):
        """Calculate hash if not provided."""
        if self.hash is None:
            self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> bytes:
        """Calculate a hash of the data point."""
        data_str = json.dumps(self.data, sort_keys=True)
        return hashlib.sha256(
            f"{self.source_id}:{self.timestamp}:{data_str}".encode()
        ).digest()


class EnvDataCollector:
    """
    Environmental Data Collector for PulseChain.
    
    This class collects data from various environmental sources to be used
    in the consensus mechanism.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the environmental data collector.
        
        Args:
            config_file: Optional path to a configuration file
        """
        # Data sources
        self.sources: Dict[str, DataSourceConfig] = {}
        
        # Collected data
        self.data_points: Dict[str, List[DataPoint]] = {}
        self.latest_data: Dict[str, DataPoint] = {}
        
        # Callbacks
        self.on_data_collected_callbacks: List[Callable[[DataPoint], None]] = []
        
        # Threading
        self.lock = threading.Lock()
        self.running = False
        self.threads: Dict[str, threading.Thread] = {}
        
        # Load configuration if provided
        if config_file and os.path.exists(config_file):
            self.load_config(config_file)
        
        logger.info("Environmental Data Collector initialized")
    
    def load_config(self, config_file: str) -> bool:
        """
        Load configuration from a file.
        
        Args:
            config_file: Path to the configuration file
            
        Returns:
            True if the configuration was loaded successfully, False otherwise
        """
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Process sources
            if 'sources' in config:
                for source_config in config['sources']:
                    source_id = source_config.get('source_id')
                    source_type_str = source_config.get('source_type')
                    
                    if not source_id or not source_type_str:
                        logger.warning(f"Invalid source configuration: {source_config}")
                        continue
                    
                    try:
                        source_type = DataSourceType(source_type_str)
                    except ValueError:
                        source_type = DataSourceType.CUSTOM
                    
                    self.add_source(
                        source_id=source_id,
                        source_type=source_type,
                        api_url=source_config.get('api_url'),
                        api_key=source_config.get('api_key'),
                        update_interval=source_config.get('update_interval', 60.0),
                        params=source_config.get('params', {})
                    )
            
            logger.info(f"Loaded configuration from {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return False
    
    def save_config(self, config_file: str) -> bool:
        """
        Save configuration to a file.
        
        Args:
            config_file: Path to the configuration file
            
        Returns:
            True if the configuration was saved successfully, False otherwise
        """
        try:
            config = {
                'sources': [
                    {
                        'source_id': source.source_id,
                        'source_type': source.source_type.value,
                        'api_url': source.api_url,
                        'api_key': source.api_key,
                        'update_interval': source.update_interval,
                        'params': source.params,
                        'enabled': source.enabled
                    }
                    for source in self.sources.values()
                ]
            }
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info(f"Saved configuration to {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def add_source(self, 
                  source_id: str, 
                  source_type: Union[DataSourceType, str],
                  api_url: Optional[str] = None,
                  api_key: Optional[str] = None,
                  update_interval: float = 60.0,
                  params: Dict[str, Any] = None) -> bool:
        """
        Add a data source.
        
        Args:
            source_id: Unique identifier for the source
            source_type: Type of data source
            api_url: URL for API-based sources
            api_key: API key for authentication
            update_interval: How often to update data from this source (in seconds)
            params: Additional parameters for the source
            
        Returns:
            True if the source was added successfully, False otherwise
        """
        with self.lock:
            # Convert string to enum if needed
            if isinstance(source_type, str):
                try:
                    source_type = DataSourceType(source_type)
                except ValueError:
                    source_type = DataSourceType.CUSTOM
            
            # Create the source
            self.sources[source_id] = DataSourceConfig(
                source_id=source_id,
                source_type=source_type,
                api_url=api_url,
                api_key=api_key,
                update_interval=update_interval,
                params=params or {}
            )
            
            # Initialize data storage
            self.data_points[source_id] = []
            
            logger.info(f"Added {source_type.value} data source: {source_id}")
            return True
    
    def remove_source(self, source_id: str) -> bool:
        """
        Remove a data source.
        
        Args:
            source_id: Identifier of the source to remove
            
        Returns:
            True if the source was removed, False if it didn't exist
        """
        with self.lock:
            if source_id not in self.sources:
                logger.warning(f"Unknown data source: {source_id}")
                return False
            
            # Stop collection thread if running
            if source_id in self.threads and self.threads[source_id].is_alive():
                # Can't directly stop a thread, but we can remove it from the running sources
                # It will terminate after the next collection cycle
                pass
            
            # Remove from sources
            del self.sources[source_id]
            
            # Remove from data storage
            if source_id in self.data_points:
                del self.data_points[source_id]
            
            if source_id in self.latest_data:
                del self.latest_data[source_id]
            
            logger.info(f"Removed data source: {source_id}")
            return True
    
    def collect_from_source(self, source_id: str) -> Optional[DataPoint]:
        """
        Collect data from a specific source.
        
        Args:
            source_id: Identifier of the source to collect from
            
        Returns:
            The collected data point, or None if collection failed
        """
        with self.lock:
            if source_id not in self.sources:
                logger.warning(f"Unknown data source: {source_id}")
                return None
            
            source = self.sources[source_id]
            
            if not source.enabled:
                logger.debug(f"Source {source_id} is disabled")
                return None
            
            try:
                # Collect data based on source type
                data = self._collect_from_source_type(source)
                
                if data:
                    # Create data point
                    data_point = DataPoint(
                        source_id=source_id,
                        source_type=source.source_type,
                        timestamp=time.time(),
                        data=data
                    )
                    
                    # Store data point
                    self.data_points[source_id].append(data_point)
                    self.latest_data[source_id] = data_point
                    
                    # Limit the number of stored data points
                    if len(self.data_points[source_id]) > 1000:
                        self.data_points[source_id] = self.data_points[source_id][-1000:]
                    
                    # Notify callbacks
                    for callback in self.on_data_collected_callbacks:
                        try:
                            callback(data_point)
                        except Exception as e:
                            logger.error(f"Error in data collected callback: {e}")
                    
                    logger.debug(f"Collected data from {source_id}")
                    return data_point
                
            except Exception as e:
                logger.error(f"Error collecting data from {source_id}: {e}")
            
            return None
    
    def _collect_from_source_type(self, source: DataSourceConfig) -> Optional[Dict[str, Any]]:
        """
        Collect data from a source based on its type.
        
        Args:
            source: The source configuration
            
        Returns:
            The collected data, or None if collection failed
        """
        if source.source_type == DataSourceType.MARKET:
            return self._collect_market_data(source)
        
        elif source.source_type == DataSourceType.WEATHER:
            return self._collect_weather_data(source)
        
        elif source.source_type == DataSourceType.TIME:
            return self._collect_time_data(source)
        
        elif source.source_type == DataSourceType.NETWORK:
            return self._collect_network_data(source)
        
        elif source.source_type == DataSourceType.SYSTEM:
            return self._collect_system_data(source)
        
        elif source.source_type == DataSourceType.CUSTOM:
            return self._collect_custom_data(source)
        
        return None
    
    def _collect_market_data(self, source: DataSourceConfig) -> Optional[Dict[str, Any]]:
        """Collect market data from an API."""
        if not source.api_url:
            return None
        
        headers = {}
        if source.api_key:
            headers["Authorization"] = f"Bearer {source.api_key}"
        
        response = requests.get(
            source.api_url, 
            headers=headers, 
            params=source.params,
            timeout=10
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Add timestamp if not present
                if "timestamp" not in data:
                    data["timestamp"] = time.time()
                
                return data
                
            except Exception as e:
                logger.error(f"Error parsing market data: {e}")
        
        return None
    
    def _collect_weather_data(self, source: DataSourceConfig) -> Optional[Dict[str, Any]]:
        """Collect weather data from an API."""
        if not source.api_url:
            return None
        
        headers = {}
        if source.api_key:
            headers["Authorization"] = f"Bearer {source.api_key}"
        
        response = requests.get(
            source.api_url, 
            headers=headers, 
            params=source.params,
            timeout=10
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Add timestamp if not present
                if "timestamp" not in data:
                    data["timestamp"] = time.time()
                
                return data
                
            except Exception as e:
                logger.error(f"Error parsing weather data: {e}")
        
        return None
    
    def _collect_time_data(self, source: DataSourceConfig) -> Optional[Dict[str, Any]]:
        """Collect time synchronization data."""
        # In a real implementation, this would query NTP servers
        # For now, we just use the current time
        
        # Get NTP servers from params or use defaults
        ntp_servers = source.params.get("ntp_servers", ["pool.ntp.org", "time.google.com"])
        
        # Simulate NTP query
        offsets = []
        for server in ntp_servers:
            try:
                # In a real implementation, this would use ntplib
                # For now, we just simulate a random offset
                offset = random.uniform(-0.01, 0.01)  # -10ms to +10ms
                offsets.append(offset)
            except Exception as e:
                logger.error(f"Error querying NTP server {server}: {e}")
        
        if not offsets:
            return None
        
        # Calculate average offset
        avg_offset = sum(offsets) / len(offsets)
        
        return {
            "timestamp": time.time(),
            "system_time": time.time(),
            "ntp_offset": avg_offset,
            "ntp_servers": ntp_servers,
            "server_offsets": dict(zip(ntp_servers, offsets))
        }
    
    def _collect_network_data(self, source: DataSourceConfig) -> Optional[Dict[str, Any]]:
        """Collect network statistics."""
        # In a real implementation, this would collect actual network stats
        # For now, we just simulate some network data
        
        # Get target hosts from params or use defaults
        target_hosts = source.params.get("target_hosts", ["8.8.8.8", "1.1.1.1"])
        
        # Ping hosts
        ping_results = {}
        for host in target_hosts:
            try:
                # In a real implementation, this would use ping
                # For now, we just simulate a random latency
                latency = random.uniform(10, 200)  # 10ms to 200ms
                ping_results[host] = latency
            except Exception as e:
                logger.error(f"Error pinging host {host}: {e}")
        
        # Measure bandwidth (simulated)
        download_speed = random.uniform(10, 100)  # 10 to 100 Mbps
        upload_speed = random.uniform(5, 50)      # 5 to 50 Mbps
        
        return {
            "timestamp": time.time(),
            "ping_results": ping_results,
            "average_latency": sum(ping_results.values()) / len(ping_results) if ping_results else None,
            "download_speed": download_speed,
            "upload_speed": upload_speed,
            "packet_loss": random.uniform(0, 0.05)  # 0% to 5%
        }
    
    def _collect_system_data(self, source: DataSourceConfig) -> Optional[Dict[str, Any]]:
        """Collect system statistics."""
        # In a real implementation, this would use psutil
        # For now, we just simulate some system data
        
        return {
            "timestamp": time.time(),
            "cpu_usage": random.uniform(0, 100),  # 0% to 100%
            "memory_usage": random.uniform(0, 100),  # 0% to 100%
            "disk_usage": random.uniform(0, 100),  # 0% to 100%
            "uptime": random.uniform(0, 86400),  # 0 to 24 hours
            "temperature": random.uniform(30, 80)  # 30°C to 80°C
        }
    
    def _collect_custom_data(self, source: DataSourceConfig) -> Optional[Dict[str, Any]]:
        """Collect data from a custom source."""
        if not source.api_url:
            return None
        
        headers = {}
        if source.api_key:
            headers["Authorization"] = f"Bearer {source.api_key}"
        
        response = requests.get(
            source.api_url, 
            headers=headers, 
            params=source.params,
            timeout=10
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Add timestamp if not present
                if "timestamp" not in data:
                    data["timestamp"] = time.time()
                
                return data
                
            except Exception as e:
                logger.error(f"Error parsing custom data: {e}")
        
        return None
    
    def collect_all_data(self) -> Dict[str, Optional[DataPoint]]:
        """
        Collect data from all sources.
        
        Returns:
            Dictionary mapping source IDs to collected data points
        """
        results = {}
        
        for source_id in list(self.sources.keys()):
            results[source_id] = self.collect_from_source(source_id)
        
        return results
    
    def get_latest_data(self, source_id: str) -> Optional[DataPoint]:
        """
        Get the latest data from a source.
        
        Args:
            source_id: Identifier of the source
            
        Returns:
            The latest data point, or None if no data has been collected
        """
        with self.lock:
            return self.latest_data.get(source_id)
    
    def get_all_latest_data(self) -> Dict[str, Optional[DataPoint]]:
        """
        Get the latest data from all sources.
        
        Returns:
            Dictionary mapping source IDs to latest data points
        """
        with self.lock:
            return dict(self.latest_data)
    
    def get_data_history(self, source_id: str, count: int = 100) -> List[DataPoint]:
        """
        Get historical data from a source.
        
        Args:
            source_id: Identifier of the source
            count: Maximum number of data points to return
            
        Returns:
            List of historical data points
        """
        with self.lock:
            if source_id not in self.data_points:
                return []
            
            return list(self.data_points[source_id])[-count:]
    
    def on_data_collected(self, callback: Callable[[DataPoint], None]) -> None:
        """
        Register a callback to be called when data is collected.
        
        Args:
            callback: The callback function
        """
        self.on_data_collected_callbacks.append(callback)
    
    def start(self) -> None:
        """Start the environmental data collector."""
        if self.running:
            logger.warning("Environmental Data Collector is already running")
            return
        
        self.running = True
        
        # Start collection threads for each source
        for source_id, source in self.sources.items():
            if source.enabled:
                thread = threading.Thread(
                    target=self._collection_thread,
                    args=(source_id,),
                    daemon=True
                )
                self.threads[source_id] = thread
                thread.start()
        
        logger.info("Environmental Data Collector started")
    
    def stop(self) -> None:
        """Stop the environmental data collector."""
        self.running = False
        
        # Wait for threads to terminate
        for source_id, thread in self.threads.items():
            if thread.is_alive():
                thread.join(timeout=2.0)
        
        self.threads.clear()
        
        logger.info("Environmental Data Collector stopped")
    
    def _collection_thread(self, source_id: str) -> None:
        """
        Collection thread for a source.
        
        Args:
            source_id: Identifier of the source
        """
        while self.running:
            try:
                # Check if source still exists and is enabled
                with self.lock:
                    if source_id not in self.sources or not self.sources[source_id].enabled:
                        break
                    
                    update_interval = self.sources[source_id].update_interval
                
                # Collect data
                self.collect_from_source(source_id)
                
                # Sleep until next collection
                time.sleep(update_interval)
                
            except Exception as e:
                logger.error(f"Error in collection thread for {source_id}: {e}")
                time.sleep(5.0)  # Sleep a bit before retrying
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the environmental data collector.
        
        Returns:
            A dictionary with status information
        """
        with self.lock:
            return {
                "sources": {
                    source_id: {
                        "type": source.source_type.value,
                        "enabled": source.enabled,
                        "update_interval": source.update_interval,
                        "data_points": len(self.data_points.get(source_id, [])),
                        "last_update": self.latest_data[source_id].timestamp if source_id in self.latest_data else None
                    }
                    for source_id, source in self.sources.items()
                },
                "total_sources": len(self.sources),
                "enabled_sources": sum(1 for source in self.sources.values() if source.enabled),
                "total_data_points": sum(len(points) for points in self.data_points.values())
            }


# Example usage
if __name__ == "__main__":
    # Create a data collector
    collector = EnvDataCollector()
    
    # Add some data sources
    collector.add_source(
        source_id="market1",
        source_type=DataSourceType.MARKET,
        api_url="https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
        update_interval=30.0
    )
    
    collector.add_source(
        source_id="weather1",
        source_type=DataSourceType.WEATHER,
        api_url="https://api.openweathermap.org/data/2.5/weather",
        params={"q": "London", "appid": "your_api_key"},
        update_interval=60.0
    )
    
    collector.add_source(
        source_id="time1",
        source_type=DataSourceType.TIME,
        update_interval=10.0
    )
    
    collector.add_source(
        source_id="network1",
        source_type=DataSourceType.NETWORK,
        update_interval=15.0
    )
    
    collector.add_source(
        source_id="system1",
        source_type=DataSourceType.SYSTEM,
        update_interval=5.0
    )
    
    # Define a callback
    def on_data_collected(data_point: DataPoint):
        print(f"Collected data from {data_point.source_id} ({data_point.source_type.value})")
    
    collector.on_data_collected(on_data_collected)
    
    # Start the collector
    collector.start()
    
    try:
        # Run for a while
        print("Collecting data for 30 seconds...")
        time.sleep(30)
        
        # Print status
        status = collector.get_status()
        print("\nStatus:")
        print(f"Total sources: {status['total_sources']}")
        print(f"Enabled sources: {status['enabled_sources']}")
        print(f"Total data points: {status['total_data_points']}")
        
        print("\nSources:")
        for source_id, source_info in status['sources'].items():
            print(f"  {source_id} ({source_info['type']}): {source_info['data_points']} data points")
            
            # Print latest data
            latest = collector.get_latest_data(source_id)
            if latest:
                print(f"    Latest data: {latest.timestamp}")
                print(f"    Data: {latest.data}")
    
    finally:
        # Stop the collector
        collector.stop()