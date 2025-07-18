"""
Inventory loader module for CSV-based device management.

This module provides functionality to load device information from CSV files
and establish connections to network devices.
"""

import csv
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Try to import pyATS components, fallback to mock if not available
try:
    from pyats.topology import loader
    from pyats.topology.lib.base import Device
    from pyats.connections import BaseConnection
    PYATS_AVAILABLE = True
except ImportError:
    # Mock classes for testing when pyATS is not available
    logger.warning("pyATS not available, using mock classes for testing")
    PYATS_AVAILABLE = False
    
    class MockDevice:
        """Mock Device class for testing when pyATS is not available."""
        def __init__(self, name, **kwargs):
            self.name = name
            self._connected = False
            self.connection_info = kwargs
            
        def is_connected(self):
            return self._connected
            
        def connect(self, **kwargs):
            self._connected = True
            logger.info(f"Mock connection to {self.name}")
            
        def disconnect(self):
            self._connected = False
            logger.info(f"Mock disconnect from {self.name}")
            
        def execute(self, command):
            return f"Mock output for command: {command}"
            
        def parse(self, command):
            return {"mock": "parsed output", "command": command}
            
        def configure(self, config):
            return f"Mock config applied: {config}"
            
        def enable(self):
            """Mock enable method for privilege escalation."""
            logger.info(f"Mock enable on {self.name}")
            return "Mock enable successful"
    
    Device = MockDevice
    loader = None

# Default CSV file path - can be overridden by environment variable
DEFAULT_CSV_PATH = os.getenv("DEVICE_INVENTORY_CSV", "device_inventory.csv")

def load_device_from_csv(device_name: str, csv_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load device information from CSV file.
    
    Expected CSV format:
    device_name,hostname,username,password,device_type,protocol,port
    router1,192.168.1.1,admin,password,cisco_ios,ssh,22
    switch1,192.168.1.2,admin,password,cisco_ios,ssh,22
    
    Args:
        device_name: Name of the device to load
        csv_path: Optional path to CSV file (defaults to environment variable or default)
    
    Returns:
        Dictionary containing device connection information
        
    Raises:
        FileNotFoundError: If CSV file is not found
        ValueError: If device is not found in CSV or CSV format is invalid
    """
    if csv_path is None:
        csv_path = DEFAULT_CSV_PATH
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Device inventory CSV file not found: {csv_path}")
    
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Validate CSV headers
            required_fields = ['device_name', 'hostname', 'username', 'password', 'device_type']
            if not all(field in reader.fieldnames for field in required_fields):
                missing_fields = [field for field in required_fields if field not in reader.fieldnames]
                raise ValueError(f"CSV file missing required fields: {missing_fields}")
            
            for row in reader:
                if row['device_name'].strip() == device_name:
                    # Set defaults for optional fields
                    device_info = {
                        'device_name': row['device_name'].strip(),
                        'hostname': row['hostname'].strip(),
                        'username': row['username'].strip(),
                        'password': row['password'].strip(),
                        'device_type': row['device_type'].strip(),
                        'protocol': row.get('protocol', 'ssh').strip(),
                        'port': int(row.get('port', 22)) if row.get('port') else 22,
                        'timeout': int(row.get('timeout', 120)) if row.get('timeout') else 120
                    }
                    logger.info(f"Loaded device info for {device_name} from CSV")
                    return device_info
            
            raise ValueError(f"Device '{device_name}' not found in CSV file: {csv_path}")
            
    except (csv.Error, ValueError) as e:
        logger.error(f"Error reading CSV file {csv_path}: {e}")
        raise ValueError(f"Error reading device inventory CSV: {e}")
    except Exception as e:
        logger.error(f"Unexpected error loading device from CSV: {e}")
        raise

def connect_to_device(device_info: Dict[str, Any]) -> Device:
    """
    Create and return a connected pyATS Device object from device information.
    
    Args:
        device_info: Dictionary containing device connection information
                    (as returned by load_device_from_csv)
    
    Returns:
        Connected pyATS Device object
        
    Raises:
        ValueError: If required device information is missing
        Exception: If connection fails
    """
    required_fields = ['device_name', 'hostname', 'username', 'password', 'device_type']
    missing_fields = [field for field in required_fields if field not in device_info]
    if missing_fields:
        raise ValueError(f"Missing required device information: {missing_fields}")
    
    try:
        if not PYATS_AVAILABLE:
            # Return mock device for testing
            device = Device(device_info['device_name'], **device_info)
            logger.info(f"Created mock device object for {device_info['device_name']}")
            return device
        
        # Create a testbed-like structure for pyATS compatibility
        testbed_dict = {
            'devices': {
                device_info['device_name']: {
                    'type': device_info['device_type'],
                    'os': device_info.get('os', 'ios'),  # Default to ios if not specified
                    'connections': {
                        'default': {
                            'protocol': device_info.get('protocol', 'ssh'),
                            'ip': device_info['hostname'],
                            'port': device_info.get('port', 22),
                            'username': device_info['username'],
                            'password': device_info['password'],
                            'connection_timeout': device_info.get('timeout', 120)
                        }
                    }
                }
            }
        }
        
        # Create testbed from dictionary
        testbed = loader.load(testbed_dict)
        device = testbed.devices[device_info['device_name']]
        
        logger.info(f"Created device object for {device_info['device_name']}")
        return device
        
    except Exception as e:
        logger.error(f"Error creating device object for {device_info['device_name']}: {e}")
        raise Exception(f"Failed to create device connection: {e}")

def create_sample_csv(csv_path: str = "device_inventory.csv") -> None:
    """
    Create a sample CSV file with example device entries.
    
    Args:
        csv_path: Path where to create the sample CSV file
    """
    sample_data = [
        {
            'device_name': 'router1',
            'hostname': '192.168.1.1',
            'username': 'admin',
            'password': 'password',
            'device_type': 'cisco_ios',
            'protocol': 'ssh',
            'port': 22,
            'timeout': 120
        },
        {
            'device_name': 'switch1',
            'hostname': '192.168.1.2',
            'username': 'admin',
            'password': 'password',
            'device_type': 'cisco_ios',
            'protocol': 'ssh',
            'port': 22,
            'timeout': 120
        },
        {
            'device_name': 'linux1',
            'hostname': '192.168.1.10',
            'username': 'root',
            'password': 'password',
            'device_type': 'linux',
            'protocol': 'ssh',
            'port': 22,
            'timeout': 120
        }
    ]
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['device_name', 'hostname', 'username', 'password', 'device_type', 'protocol', 'port', 'timeout']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(sample_data)
    
    logger.info(f"Created sample CSV file: {csv_path}")