# pyATS Custom MCP Server with CSV Inventory

This repository contains a Model Context Protocol (MCP) server that provides network automation capabilities using pyATS with CSV-based device inventory.

## Overview

The MCP server has been updated to use CSV-based device inventory instead of pyATS testbed files. This approach provides more flexibility and easier device management.

## CSV Inventory Format

The device inventory is stored in a CSV file with the following format:

```csv
device_name,hostname,username,password,device_type,protocol,port,timeout
router1,192.168.1.1,admin,password,cisco_ios,ssh,22,120
switch1,192.168.1.2,admin,password,cisco_ios,ssh,22,120
linux1,192.168.1.10,root,password,linux,ssh,22,120
firewall1,192.168.1.254,admin,admin123,cisco_asa,ssh,22,120
```

### Required Fields
- `device_name`: Unique name for the device
- `hostname`: IP address or hostname of the device
- `username`: Login username
- `password`: Login password
- `device_type`: Device type (cisco_ios, cisco_nxos, linux, etc.)

### Optional Fields
- `protocol`: Connection protocol (default: ssh)
- `port`: Connection port (default: 22)
- `timeout`: Connection timeout in seconds (default: 120)

## Environment Variables

- `DEVICE_INVENTORY_CSV`: Path to the CSV inventory file (default: device_inventory.csv)

## Features

The server provides the following MCP tools:

1. **pyats_run_show_command**: Execute show commands on network devices
2. **pyats_configure_device**: Apply configuration to devices
3. **pyats_show_running_config**: Retrieve running configuration
4. **pyats_show_logging**: Get system logs
5. **pyats_ping_from_network_device**: Execute ping commands
6. **pyats_run_linux_command**: Execute Linux commands

## Changes from Testbed-based Approach

### Before (Testbed-based)
```python
testbed = loader.load(TESTBED_PATH)
device = testbed.devices[device_name]
device.connect()
```

### After (CSV-based)
```python
from helpers.inventory_loader import load_device_from_csv, connect_to_device

device_row = load_device_from_csv(device_name)
device = connect_to_device(device_row)
device.connect()
```

## Dependencies

- pyATS/Genie (optional - mock classes provided for testing)
- python-dotenv (optional)
- pydantic (optional - basic validation provided)
- MCP FastMCP (optional - mock server for testing)

The code includes graceful handling of missing dependencies for development and testing purposes.

## Usage

1. Create or update your device inventory CSV file
2. Set the `DEVICE_INVENTORY_CSV` environment variable (optional)
3. Run the MCP server:

```bash
python3 mcp_pyats_custom.py
```

## Testing

The repository includes comprehensive testing with mock classes when pyATS is not available. All functionality has been verified to work correctly with the new CSV-based approach.