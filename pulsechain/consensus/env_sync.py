#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PulseChain - Environmental Synchronization
=========================================

This module implements the environmental data integration for PulseChain's PoH consensus.
It collects, validates, and integrates environmental data from various sources.
"""

import time
import hashlib
import json
import threading
import logging
import random
import statistics
from typing import Dict, List, Optional, Any, Tuple, Set, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import requests

from ..core.poh_generator import PoHGenerator
from .poh import PoHConsensus, PoHSlot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("env_sync")


class EnvDataSourceType(Enum):
    """Types of environmental data sources."""
    MARKET = "market"
    WEATHER = "weather"
    TIME = "time"
    NETWORK = "network"
    CUSTOM = "custom"


@dataclass
class EnvDataSource:
    """Configuration for an environmental data source."""
    source_type: EnvDataSourceType
    api_url: Optional[str] = None
    update_interval: float = 60.0  # seconds
    weight: float = 1.0
    last_update: float = 0.0
    last_data: Optional[Dict[str, Any]] = None
    error_count: int = 0
    max_errors: int = 5
    auth_token: Optional[str] = None
    custom_params: Optional[Dict[str, Any]] = None


@dataclass
class EnvData:
    """Environmental data collected from various sources."""
    timestamp: float
    source_id: str
    data: Dict[str, Any]
    source_type: EnvDataSourceType
    confidence: float = 1.0
    hash: Optional[bytes] = None
    
    def __post_init__(self):
        """Calculate hash if not provided."""
        if self.hash is None:
            self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> bytes:
        """Calculate a hash of the environmental data."""
        data_str = json.dumps(self.data, sort_keys=True)
        return hashlib.sha256(
            f"{self.timestamp}:{self.source_id}:{data_str}".encode()
        ).digest()


class EnvDataIntegrator:
    """
    Environmental Data Integrator for PulseChain.
    
    This class collects, validates, and integrates environmental data from various sources
    into the PoH consensus mechanism.
    """
    
    def __init__(self, 
                 poh_consensus: PoHConsensus,
                 min_sources: int = 1,
                 max_data_age: float = 300.0):  # 5 minutes
        """
        Initialize the environmental data integrator.
        
        Args:
            poh_consensus: The PoH consensus mechanism to integrate with
            min_sources: Minimum number of data sources required for integration
            max_data_age: Maximum age of data to consider valid (in seconds)
        """
        self.poh_consensus = poh_consensus
        self.min_sources = min_sources
        self.max_data_age = max_data_age
        
        # Data sources
        self.sources: Dict[str, EnvDataSource] = {}
        
        # Collected data
        self.data_points: List[EnvData] = []
        self.latest_integrated_data: Optional[Dict[str, Any]] = None
        
        # Threading
        self.lock = threading.Lock()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # Register with PoH consensus
        self.poh_consensus.on_new_slot(self._on_new_slot)
        
        logger.info("Environmental Data Integrator initialized")
    
    def add_source(self, 
                  source_id: str, 
                  source_type: Union[EnvDataSourceType, str],
                  api_url: Optional[str] = None,
                  update_interval: float = 60.0,
                  weight: float = 1.0,
                  auth_token: Optional[str] = None,
                  custom_params: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a data source.
        
        Args:
            source_id: Unique identifier for the source
            source_type: Type of data source
            api_url: URL for API-based sources
            update_interval: How often to update data from this source (in seconds)
            weight: Weight of this source in the integration (0.0 to 1.0)
            auth_token: Optional authentication token for API access
            custom_params: Optional custom parameters for the source
            
        Returns:
            True if the source was added successfully, False otherwise
        """
        with self.lock:
            # Convert string to enum if needed
            if isinstance(source_type, str):
                try:
                    source_type = EnvDataSourceType(source_type)
                except ValueError:
                    source_type = EnvDataSourceType.CUSTOM
            
            # Create the source
            self.sources[source_id] = EnvDataSource(
                source_type=source_type,
                api_url=api_url,
                update_interval=update_interval,
                weight=weight,
                auth_token=auth_token,
                custom_params=custom_params
            )
            
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
            if source_id in self.sources:
                del self.sources[source_id]
                logger.info(f"Removed data source: {source_id}")
                return True
            return False
    
    def collect_data(self, source_id: str) -> Optional[EnvData]:
        """
        Collect data from a specific source.
        
        Args:
            source_id: Identifier of the source to collect from
            
        Returns:
            The collected data, or None if collection failed
        """
        with self.lock:
            if source_id not in self.sources:
                logger.warning(f"Unknown data source: {source_id}")
                return None
            
            source = self.sources[source_id]
            
            # Check if it's time to update
            current_time = time.time()
            if current_time - source.last_update < source.update_interval:
                # Use cached data if available
                if source.last_data:
                    return EnvData(
                        timestamp=source.last_update,
                        source_id=source_id,
                        data=source.last_data,
                        source_type=source.source_type,
                        confidence=max(0.5, 1.0 - (current_time - source.last_update) / self.max_data_age)
                    )
                return None
            
            try:
                # Collect data based on source type
                data = self._collect_from_source(source, source_id)
                
                if data:
                    # Update source state
                    source.last_update = current_time
                    source.last_data = data
                    source.error_count = 0
                    
                    # Create and return EnvData
                    return EnvData(
                        timestamp=current_time,
                        source_id=source_id,
                        data=data,
                        source_type=source.source_type,
                        confidence=1.0
                    )
                
            except Exception as e:
                logger.error(f"Error collecting data from {source_id}: {e}")
                source.error_count += 1
                
                # If too many errors, reduce confidence but still try to use cached data
                if source.error_count > source.max_errors and source.last_data:
                    confidence = max(0.1, 1.0 - (source.error_count / 10))
                    return EnvData(
                        timestamp=source.last_update,
                        source_id=source_id,
                        data=source.last_data,
                        source_type=source.source_type,
                        confidence=confidence
                    )
            
            return None
    
    def _collect_from_source(self, source: EnvDataSource, source_id: str) -> Optional[Dict[str, Any]]:
        """
        Collect data from a specific source based on its type.
        
        Args:
            source: The source configuration
            source_id: Identifier of the source
            
        Returns:
            The collected data, or None if collection failed
        """
        if source.source_type == EnvDataSourceType.MARKET:
            return self._collect_market_data(source)
        
        elif source.source_type == EnvDataSourceType.WEATHER:
            return self._collect_weather_data(source)
        
        elif source.source_type == EnvDataSourceType.TIME:
            return self._collect_time_data(source)
        
        elif source.source_type == EnvDataSourceType.NETWORK:
            return self._collect_network_data(source)
        
        elif source.source_type == EnvDataSourceType.CUSTOM:
            return self._collect_custom_data(source, source_id)
        
        return None
    
    def _collect_market_data(self, source: EnvDataSource) -> Optional[Dict[str, Any]]:
        """Collect market data from an API."""
        if not source.api_url:
            return None
        
        headers = {}
        if source.auth_token:
            headers["Authorization"] = f"Bearer {source.auth_token}"
        
        response = requests.get(source.api_url, headers=headers, timeout=5)
        if response.status_code == 200:
            try:
                data = response.json()
                # Extract relevant market data
                market_data = {
                    "timestamp": time.time()
                }
                
                # Look for common market data fields
                for key in ["price", "prices", "rates", "exchange_rates", "market_data"]:
                    if key in data:
                        market_data[key] = data[key]
                
                # If we found any data, return it
                if len(market_data) > 1:  # More than just timestamp
                    return market_data
                
                # Otherwise, return the whole response
                return data
                
            except Exception as e:
                logger.error(f"Error parsing market data: {e}")
        
        return None
    
    def _collect_weather_data(self, source: EnvDataSource) -> Optional[Dict[str, Any]]:
        """Collect weather data from an API."""
        if not source.api_url:
            return None
        
        headers = {}
        if source.auth_token:
            headers["Authorization"] = f"Bearer {source.auth_token}"
        
        # Get location from custom params or use default
        params = {}
        if source.custom_params:
            if "lat" in source.custom_params and "lon" in source.custom_params:
                params["lat"] = source.custom_params["lat"]
                params["lon"] = source.custom_params["lon"]
            elif "city" in source.custom_params:
                params["q"] = source.custom_params["city"]
        
        response = requests.get(source.api_url, headers=headers, params=params, timeout=5)
        if response.status_code == 200:
            try:
                data = response.json()
                # Extract relevant weather data
                weather_data = {
                    "timestamp": time.time()
                }
                
                # Look for common weather data fields
                for key in ["temp", "temperature", "humidity", "pressure", "wind", "weather"]:
                    if key in data:
                        weather_data[key] = data[key]
                
                # If we found any data, return it
                if len(weather_data) > 1:  # More than just timestamp
                    return weather_data
                
                # Otherwise, return the whole response
                return data
                
            except Exception as e:
                logger.error(f"Error parsing weather data: {e}")
        
        return None
    
    def _collect_time_data(self, source: EnvDataSource) -> Optional[Dict[str, Any]]:
        """Collect time synchronization data."""
        # For time data, we just use the current time
        # In a real implementation, this would query NTP servers
        return {
            "timestamp": time.time(),
            "system_time": time.time(),
            "ntp_offset": 0.0  # Simulated NTP offset
        }
    
    def _collect_network_data(self, source: EnvDataSource) -> Optional[Dict[str, Any]]:
        """Collect network statistics."""
        # In a real implementation, this would collect actual network stats
        return {
            "timestamp": time.time(),
            "latency": random.uniform(50, 200),  # ms
            "packet_loss": random.uniform(0, 0.02),  # 0-2%
            "bandwidth": random.uniform(10, 100)  # Mbps
        }
    
    def _collect_custom_data(self, source: EnvDataSource, source_id: str) -> Optional[Dict[str, Any]]:
        """Collect data from a custom source."""
        if not source.api_url:
            return None
        
        headers = {}
        if source.auth_token:
            headers["Authorization"] = f"Bearer {source.auth_token}"
        
        response = requests.get(
            source.api_url, 
            headers=headers, 
            params=source.custom_params, 
            timeout=5
        )
        
        if response.status_code == 200:
            try:
                data = response.json()
                # Add timestamp if not present
                if "timestamp" not in data:
                    data["timestamp"] = time.time()
                return data
            except Exception as e:
                logger.error(f"Error parsing custom data from {source_id}: {e}")
        
        return None
    
    def collect_all_data(self) -> List[EnvData]:
        """
        Collect data from all sources.
        
        Returns:
            List of collected data points
        """
        collected = []
        
        for source_id in list(self.sources.keys()):
            data = self.collect_data(source_id)
            if data:
                collected.append(data)
                self.data_points.append(data)
        
        # Limit the number of stored data points
        if len(self.data_points) > 1000:
            self.data_points = self.data_points[-1000:]
        
        return collected
    
    def integrate_data(self) -> Optional[Dict[str, Any]]:
        """
        Integrate collected data into a single environmental data point.
        
        Returns:
            Integrated data, or None if not enough data is available
        """
        with self.lock:
            # Filter out old data
            current_time = time.time()
            valid_data = [
                d for d in self.data_points 
                if current_time - d.timestamp <= self.max_data_age
            ]
            
            if len(valid_data) < self.min_sources:
                logger.warning(
                    f"Not enough valid data sources: {len(valid_data)} < {self.min_sources}"
                )
                return None
            
            # Group data by source type
            by_type: Dict[EnvDataSourceType, List[EnvData]] = {}
            for data in valid_data:
                if data.source_type not in by_type:
                    by_type[data.source_type] = []
                by_type[data.source_type].append(data)
            
            # Integrate data by type
            integrated = {
                "timestamp": current_time,
                "source_count": len(valid_data),
                "integrated_by": self.poh_consensus.node_id
            }
            
            # Process each type
            for source_type, data_list in by_type.items():
                type_key = source_type.value
                integrated[type_key] = self._integrate_by_type(data_list)
            
            # Calculate a combined hash of all data
            integrated_hash = hashlib.sha256(
                json.dumps(integrated, sort_keys=True).encode()
            ).digest()
            
            integrated["hash"] = integrated_hash.hex()
            
            self.latest_integrated_data = integrated
            return integrated
    
    def _integrate_by_type(self, data_list: List[EnvData]) -> Dict[str, Any]:
        """
        Integrate data of the same type.
        
        Args:
            data_list: List of data points of the same type
            
        Returns:
            Integrated data for this type
        """
        if not data_list:
            return {}
        
        # Sort by confidence
        data_list.sort(key=lambda d: d.confidence, reverse=True)
        
        # For simple numeric values, use weighted average
        result = {}
        
        # Collect all keys from all data points
        all_keys = set()
        for data in data_list:
            all_keys.update(data.data.keys())
        
        # Process each key
        for key in all_keys:
            # Skip timestamp key
            if key == "timestamp":
                continue
            
            # Collect values for this key
            values = []
            weights = []
            
            for data in data_list:
                if key in data.data and isinstance(data.data[key], (int, float)):
                    values.append(data.data[key])
                    weights.append(data.confidence)
            
            if values:
                # Calculate weighted average
                if len(values) == 1:
                    result[key] = values[0]
                else:
                    # Check for outliers
                    if len(values) >= 4:
                        # Use median absolute deviation to detect outliers
                        median = statistics.median(values)
                        deviations = [abs(x - median) for x in values]
                        mad = statistics.median(deviations)
                        
                        # Filter out values more than 3 MADs from the median
                        filtered_values = []
                        filtered_weights = []
                        
                        for i, value in enumerate(values):
                            if abs(value - median) <= 3 * mad:
                                filtered_values.append(value)
                                filtered_weights.append(weights[i])
                        
                        if filtered_values:
                            values = filtered_values
                            weights = filtered_weights
                    
                    # Calculate weighted average
                    result[key] = sum(v * w for v, w in zip(values, weights)) / sum(weights)
            
            # For non-numeric values, use the value from the highest confidence source
            else:
                for data in data_list:
                    if key in data.data:
                        result[key] = data.data[key]
                        break
        
        return result
    
    def _on_new_slot(self, slot: PoHSlot) -> None:
        """
        Callback for when a new PoH slot is created.
        
        Args:
            slot: The new slot
        """
        # Only integrate data if we're the leader for this slot
        if self.poh_consensus.is_leader:
            # Collect and integrate data
            self.collect_all_data()
            integrated = self.integrate_data()
            
            if integrated:
                # Update the PoH generator with the integrated data
                self.poh_consensus.poh_generator.next(integrated)
                logger.debug(f"Integrated environmental data into slot {slot.slot_number}")
    
    def start(self) -> None:
        """Start the environmental data integrator."""
        if self.running:
            logger.warning("Environmental Data Integrator is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info("Environmental Data Integrator started")
    
    def stop(self) -> None:
        """Stop the environmental data integrator."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
        logger.info("Environmental Data Integrator stopped")
    
    def _run(self) -> None:
        """Run the environmental data integrator."""
        while self.running:
            # Collect data periodically, even if we're not the leader
            self.collect_all_data()
            
            # Sleep for a bit
            time.sleep(1.0)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the environmental data integrator.
        
        Returns:
            A dictionary with status information
        """
        with self.lock:
            return {
                "sources": {
                    source_id: {
                        "type": source.source_type.value,
                        "last_update": source.last_update,
                        "update_interval": source.update_interval,
                        "error_count": source.error_count
                    }
                    for source_id, source in self.sources.items()
                },
                "data_points": len(self.data_points),
                "latest_integration_time": (
                    self.latest_integrated_data["timestamp"] 
                    if self.latest_integrated_data else None
                )
            }


# Example usage
if __name__ == "__main__":
    from ..core.poh_generator import PoHGenerator
    
    # Create a PoH generator and consensus
    poh_generator = PoHGenerator(target_hash_rate=10000)
    poh_consensus = PoHConsensus(
        node_id="node1",
        region="us-west",
        poh_generator=poh_generator
    )
    
    # Create the environmental data integrator
    env_integrator = EnvDataIntegrator(poh_consensus)
    
    # Add some data sources
    env_integrator.add_source(
        source_id="weather1",
        source_type=EnvDataSourceType.WEATHER,
        api_url="https://api.openweathermap.org/data/2.5/weather",
        custom_params={"city": "San Francisco"}
    )
    
    env_integrator.add_source(
        source_id="market1",
        source_type=EnvDataSourceType.MARKET,
        api_url="https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    )
    
    env_integrator.add_source(
        source_id="time1",
        source_type=EnvDataSourceType.TIME
    )
    
    # Start the components
    poh_consensus.start()
    env_integrator.start()
    
    try:
        # Run for a while
        for _ in range(5):
            time.sleep(1)
            status = env_integrator.get_status()
            print(f"Data points: {status['data_points']}")
            
            # Simulate being the leader
            poh_consensus.is_leader = True
            
            # Create a new slot
            slot = poh_consensus.create_new_slot()
            print(f"Created slot {slot.slot_number}")
            
            # Wait for data to be integrated
            time.sleep(0.5)
            
            # Check if data was integrated
            if env_integrator.latest_integrated_data:
                print("Data integrated successfully")
                print(f"Integrated data hash: {env_integrator.latest_integrated_data.get('hash', 'N/A')}")
            else:
                print("No data integrated")
    
    finally:
        # Stop the components
        env_integrator.stop()
        poh_consensus.stop()