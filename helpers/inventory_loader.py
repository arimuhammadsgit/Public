"""
Inventory loader module for loading device information from CSV and creating connections.
"""

import csv
import os
import logging
from typing import Dict, Any, Optional
from pyats.topology import loader
from pyats.topology.loader.base import Device

logger = logging.getLogger(__name__)

def load_device_from_csv(device_name: str, csv_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load device information from CSV file or fallback to testbed.
    
    Args:
        device_name: Name of the device to load
        csv_path: Optional path to CSV file containing device inventory
        
    Returns:
        Dictionary containing device information
        
    Raises:
        ValueError: If device is not found
    """
    
    # For now, we'll use a fallback to the existing testbed approach
    # In a real implementation, this would read from a CSV file
    # This maintains compatibility with the existing system while providing the new interface
    
    try:
        # Get testbed path from environment (same as current code)
        testbed_path = os.getenv("PYATS_TESTBED_PATH")
        if not testbed_path or not os.path.exists(testbed_path):
            raise ValueError(f"PYATS_TESTBED_PATH not set or file not found: {testbed_path}")
            
        # Load testbed and extract device info
        testbed = loader.load(testbed_path)
        device = testbed.devices.get(device_name)
        
        if not device:
            raise ValueError(f"Device '{device_name}' not found in testbed '{testbed_path}'.")
            
        # Return device information in a standardized format
        device_info = {
            'name': device.name,
            'device': device,  # Keep reference to original device for compatibility
            'host': getattr(device, 'host', None),
            'os': getattr(device, 'os', None),
            'type': getattr(device, 'type', None),
            'credentials': getattr(device, 'credentials', {}),
            'connections': getattr(device, 'connections', {})
        }
        
        logger.info(f"Loaded device information for {device_name}")
        return device_info
        
    except Exception as e:
        logger.error(f"Error loading device {device_name}: {e}")
        raise


def connect_to_device(device_row: Dict[str, Any]) -> Device:
    """
    Create connection to device using device information.
    
    Args:
        device_row: Dictionary containing device information from load_device_from_csv
        
    Returns:
        Connected device object
        
    Raises:
        Exception: If connection fails
    """
    
    try:
        # Extract the device object from the row
        device = device_row['device']
        
        if not device:
            raise ValueError(f"No device object found in device_row for {device_row.get('name', 'unknown')}")
            
        logger.info(f"Creating connection wrapper for device {device.name}")
        
        # Return a connection wrapper that provides the interface expected by the calling code
        return DeviceConnectionWrapper(device)
        
    except Exception as e:
        logger.error(f"Error creating connection for device: {e}")
        raise


class DeviceConnectionWrapper:
    """
    Wrapper class to provide a consistent interface for device connections.
    This maintains compatibility with the expected interface while using pyATS devices.
    """
    
    def __init__(self, device: Device):
        self.device = device
        self.name = device.name
        
    def connect(self, **kwargs):
        """Connect to the device."""
        if not self.device.is_connected():
            logger.info(f"Connecting to {self.name}...")
            connection_kwargs = {
                'connection_timeout': 120,
                'learn_hostname': True,
                'log_stdout': False,
                'mit': True
            }
            connection_kwargs.update(kwargs)
            self.device.connect(**connection_kwargs)
            logger.info(f"Connected to {self.name}")
        else:
            logger.info(f"{self.name} is already connected")
            
    def disconnect(self):
        """Disconnect from the device."""
        if self.device.is_connected():
            logger.info(f"Disconnecting from {self.name}...")
            try:
                self.device.disconnect()
                logger.info(f"Disconnected from {self.name}")
            except Exception as e:
                logger.warning(f"Error disconnecting from {self.name}: {e}")
                
    def execute(self, command: str):
        """Execute a command on the device."""
        return self.device.execute(command)
        
    def parse(self, command: str):
        """Parse a command on the device."""
        return self.device.parse(command)
        
    def configure(self, config: str):
        """Configure the device."""
        return self.device.configure(config)
        
    def is_connected(self):
        """Check if device is connected."""
        return self.device.is_connected()
        
    def enable(self):
        """Enable privileged mode if supported."""
        if hasattr(self.device, 'enable'):
            return self.device.enable()
            
    def __getattr__(self, name):
        """Delegate any other attributes to the underlying device."""
        return getattr(self.device, name)