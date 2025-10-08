# POSTe-N Python Modules Documentation

This document provides comprehensive documentation for all Python modules in the POSTe-N project, excluding `main.py` and the `tests/` directory.

---

## Module: `commands.py`

### Overview
Handles LoRa wireless communication through AT commands and provides a serial message processing system with pattern-based message handlers.

### Purpose
Manages LoRa node communication, AT command transmission, serial message parsing, and implements a command pattern for handling different types of serial responses.

### Dependencies
- `serial`: Serial communication library
- `datetime`: For timestamping messages
- `enum`: For AT command definitions
- `dataclasses`: For structured data classes
- `abc`: For abstract base classes
- `logs.EventType`: Custom event type enumeration

### Constants
- `CMSG_AWK_REPLY_OK`: Predefined reply format for successful CMSG acknowledgments

### Enums

#### `AT`
Defines LoRa AT command constants:
- `AT = "AT"`: Basic AT command for status check
- `OK = "AT+OK"`: OK response command  
- `MSG = "AT+MSG"`: One-way message command
- `JOIN = "AT+JOIN"`: Network join command (with acknowledgment)
- `CMSG = "AT+CMSG"`: Confirmed message command (with acknowledgment)

### Data Classes

#### `ReplyFormat`
Defines the structure for expected reply patterns:
- `start: str`: Starting marker for message detection
- `end: str`: Ending marker for message completion
- `type: EventType`: Event type classification for logging

#### `SerialMessage`
Represents a complete serial message:
- `lines: list[str]`: List of message lines received
- `timestamp: datetime`: Auto-generated timestamp (defaults to current time)

### Functions

#### `get_command(cmd)`
**Purpose**: Extracts the string value from an AT command enum.

**Parameters**:
- `cmd`: AT command enum value

**Returns**: `str` - The string representation of the command

#### `write_to_serial(port, command, arg=None)`
**Purpose**: Writes AT commands to the serial port with optional arguments.

**Parameters**:
- `port`: `serial.Serial` object for communication
- `command`: AT command from the AT enum
- `arg`: Optional string argument for parameterized commands

**Behavior**:
- Formats command with argument if provided (using `="argument"` format)
- Prints payload for debugging (TODO: Remove in production)
- Adds newline terminator and encodes as ASCII
- Writes to the serial port

### Classes

#### `MessageHandler` (Abstract Base Class)
**Purpose**: Abstract base class for implementing message processing handlers using the Command pattern.

**Constructor Parameters**:
- `reply_format: ReplyFormat`: Defines the message pattern this handler processes

**Methods**:

##### `can_handle(line: str) -> bool` [@final]
- **Purpose**: Determines if this handler should process a given line
- **Logic**: Checks if line starts with the configured start marker
- **Returns**: Boolean indicating if handler can process the line

##### `feed(line: str, buffer: list[str]) -> tuple[bool, Union[SerialMessage, None]]` [@final]
- **Purpose**: Collects lines until a complete message is received
- **Parameters**:
  - `line`: Current line from serial port
  - `buffer`: Accumulator for message lines
- **Logic**: 
  - Appends line to buffer
  - Checks for end marker to determine message completion
  - Creates SerialMessage when complete and clears buffer
- **Returns**: Tuple of (completion_status, message_or_none)

##### `process(msg: SerialMessage)` [@abstractmethod]
- **Purpose**: Abstract method for processing complete messages
- **Must be implemented by concrete handler classes**

#### `CMessageOkHandler`
**Purpose**: Concrete implementation for handling successful CMSG acknowledgments.

**Inheritance**: Extends `MessageHandler`

**Constructor**: Initializes with `CMSG_AWK_REPLY_OK` reply format

**Implementation**:
- `process(msg: SerialMessage)`: Prints received message lines with formatting

#### `SerialDispatcher`
**Purpose**: Main dispatcher class that manages multiple message handlers and processes incoming serial data.

**Constructor Parameters**:
- `port: serial.Serial`: Serial communication port
- `handlers: Optional[list[MessageHandler]]`: List of message handlers (defaults to empty list)

**Attributes**:
- `port`: Serial port reference
- `handlers`: List of registered message handlers
- `buffer`: Current message buffer
- `active_handler`: Currently active handler (if any)

**Methods**:

##### `run()`
**Purpose**: Main processing loop for handling incoming serial data.

**Behavior**:
- Runs infinite loop checking for incoming serial data
- Reads and processes lines from serial port
- Implements state machine logic:
  - **No Active Handler**: Searches for handler that can process the line
  - **Active Handler**: Continues collecting data for current message
- Processes complete messages and resets handler state
- Includes debug printing (TODO: Remove in production)

### Design Patterns
- **Command Pattern**: MessageHandler system allows different processing strategies
- **State Machine**: SerialDispatcher manages handler activation/deactivation
- **Template Method**: MessageHandler provides template with abstract process method

### Usage Example
```python
# Setup handlers and dispatcher
handlers = [CMessageOkHandler()]
dispatcher = SerialDispatcher(serial_port, handlers)

# Send command and process responses
write_to_serial(port, AT.CMSG, "Hello World")
dispatcher.run()  # Processes incoming responses
```

---

## Module: `configs.py`

### Overview
Provides XML configuration file parsing utilities with specialized support for serial communication parameters and string values.

### Purpose
Handles reading and parsing of XML configuration files, with automatic type conversion and validation for serial communication settings.

### Dependencies
- `xml.etree.ElementTree`: XML parsing functionality
- `serial`: PySerial library for serial communication constants

### Constants

#### Hardware Communication Commands
- `DRRG_COMM_0 = b'\x01\x03\x00\x00\x00\x10\x44\x06'`: 
  - Digital Rain and Rain Gauge communication command
  - Purpose: Read rain and accumulated rain values
  - Format: Modbus RTU command bytes

- `DSG_COMM_0 = b'\x01\x03\x00\x00\x00\x02\xC4\x0B'`:
  - Digital Staff Gauge communication command  
  - Purpose: Read water level measurements
  - Format: Modbus RTU command bytes

#### Serial Parameter Mapping
`KEY_MAPPING` dictionary provides string-to-constant translation for serial parameters:

**Parity Options**:
- `'PARITY_NONE'` → `serial.PARITY_NONE`
- `'PARITY_ODD'` → `serial.PARITY_ODD`
- `'PARITY_EVEN'` → `serial.PARITY_EVEN`
- `'PARITY_MARK'` → `serial.PARITY_MARK`
- `'PARITY_SPACE'` → `serial.PARITY_SPACE`

**Stop Bits Options**:
- `'STOPBITS_ONE'` → `serial.STOPBITS_ONE`
- `'STOPBITS_ONE_POINT_FIVE'` → `serial.STOPBITS_ONE_POINT_FIVE`
- `'STOPBITS_TWO'` → `serial.STOPBITS_TWO`

**Data Bits Options**:
- `'FIVEBITS'` → `serial.FIVEBITS`
- `'SIXBITS'` → `serial.SIXBITS`
- `'SEVENBITS'` → `serial.SEVENBITS`
- `'EIGHTBITS'` → `serial.EIGHTBITS`

### Functions

#### `verify_unique_xml_value(key, value)`
**Purpose**: Validates and converts XML configuration values to appropriate types for serial communication.

**Parameters**:
- `key`: Configuration parameter name
- `value`: Raw string value from XML

**Logic**:
1. Checks if value exists in `KEY_MAPPING` and converts to serial constant
2. For non-mapped values, converts numeric strings to integers
3. Validates parameter by attempting to create Serial object with the parameter
4. Returns the converted value

**Returns**: Converted value (serial constant or integer)

**Side Effect**: Validates parameter compatibility by creating temporary Serial object

#### `_read_config(file_path)`
**Purpose**: Reads complete XML configuration file into nested dictionary structure.

**Parameters**:
- `file_path`: Path to XML configuration file

**Returns**: `dict` - Nested dictionary with section-based organization
- Top level keys: Section names from XML
- Second level: Parameter name-value pairs within each section

**Structure**:
```python
{
    'section_name': {
        'parameter1': 'value1',
        'parameter2': 'value2'
    }
}
```

#### `parse_serial_config(file_path, subfield) -> dict`
**Purpose**: Parses specific XML section for serial communication configuration with type conversion and validation.

**Parameters**:
- `file_path`: Path to XML configuration file
- `subfield`: XML section name to parse (Note: Parameter name suggests it should be renamed)

**Logic**:
1. Parses XML and finds specified section
2. Returns empty dict if section not found (TODO: Should raise error)
3. For each parameter in section:
   - Applies `verify_unique_xml_value()` for type conversion and validation
   - Additional numeric conversion for digit strings
4. Returns validated configuration dictionary

**Returns**: `dict` - Configuration parameters with proper types for serial communication

**Known Issues**:
- TODO comment indicates `subfield` parameter should be renamed
- TODO comment indicates error should be raised when section is missing

#### `parse_string_config(file_path: str, subfield: str) -> str`
**Purpose**: Extracts simple string value from XML configuration file.

**Parameters**:
- `file_path: str`: Path to XML configuration file
- `subfield: str`: Name of XML element containing the target string

**Logic**:
1. Parses XML file and gets root element
2. Iterates through top-level sections
3. Returns text content when matching section tag is found
4. Returns empty string if section not found

**Returns**: `str` - Text content of specified XML element, or empty string if not found

### Usage Examples

#### Serial Configuration
```python
# Parse serial settings from XML
serial_config = parse_serial_config('config.xml', 'rpi')
# Returns: {'baudrate': 9600, 'parity': serial.PARITY_NONE, ...}

# Create serial connection with parsed config
import serial
port = serial.Serial(**serial_config)
```

#### String Configuration
```python
# Get file path from configuration
log_path = parse_string_config('config.xml', 'datalogpath')
# Returns: '/path/to/data.log'
```

#### Example XML Structure
```xml
<?xml version="1.0"?>
<config>
    <rpi>
        <baudrate>9600</baudrate>
        <parity>PARITY_NONE</parity>
        <bytesize>EIGHTBITS</bytesize>
        <stopbits>STOPBITS_ONE</stopbits>
    </rpi>
    <datalogpath>/home/user/data.log</datalogpath>
</config>
```

### Error Handling
- `verify_unique_xml_value()`: May raise exceptions from Serial object creation during validation
- `parse_serial_config()`: Returns empty dict for missing sections (should be improved)
- `parse_string_config()`: Returns empty string for missing sections

---

## Module: `data.py`

### Overview
Provides data structures and utility functions for sensor data management, payload formatting, and data serialization for digital sensors (rain gauge and staff gauge).

### Purpose
Defines standardized data formats, handles sensor data collection and storage, formats data for transmission payloads, and manages null value representation.

### Dependencies
- `dataclasses`: For structured data classes
- `datetime`: For timestamping sensor readings
- `enum`: For data source enumeration
- `typing.NewType`, `typing.Optional`: For type definitions

### Constants and Type Definitions

#### Data Formatting
- `NULL_FORMAT = '#'`: Character used as placeholder for missing data

#### Data Format Types
- `_DataFormat = NewType('_DataFormat', str)`: Type alias for data format strings
- `FLOOD_FORMAT = _DataFormat("5.0")`: Format for flood/water level data (5 digits, 0 decimals)
- `RAIN_DATA_FORMAT = _DataFormat("4.2")`: Format for rainfall rate data (4 whole digits, 2 decimal places)
- `RAIN_ACCU_FORMAT = _DataFormat("4.17")`: Format for accumulated rainfall (4 whole digits, 17 decimal places)

### Enums

#### `DataSource`
Defines sensor types:
- `DIGITAL_RAIN_GAUGE = 'DRRG'`: Digital rain and rain gauge sensor
- `DIGITAL_STAFF_GAUGE = 'DSG'`: Digital staff gauge (water level sensor)

### Data Classes

#### `RawData`
**Purpose**: Represents a single sensor measurement with its formatting requirements.

**Attributes**:
- `format: _DataFormat`: Specifies how the data should be formatted for transmission
- `datum: Optional[float]`: The actual measurement value (None for missing data)

#### `SensorData`
**Purpose**: Container for multiple measurements from a single sensor with metadata.

**Attributes**:
- `source: DataSource`: Identifies the sensor type
- `unit: str`: Measurement unit (TODO: Consider removal)
- `date: datetime`: Timestamp of the sensor reading
- `data: list[RawData]`: List of raw measurements

**Methods**:

##### `append_data(datum: RawData)`
- **Purpose**: Adds a new measurement to the sensor data
- **Parameters**: `datum` - RawData object containing measurement and format

##### `get_payload_format() -> str`
- **Purpose**: Formats all measurements for transmission payload
- **Logic**: 
  - Iterates through all RawData objects
  - Uses null format for None values
  - Applies zero-padding for actual values
- **Returns**: Concatenated string of formatted measurements

##### `get_datum() -> list[float]`
- **Purpose**: Extracts raw measurement values
- **Returns**: List of float values from all RawData objects

#### `CompiledSensorData`
**Purpose**: Aggregates data from multiple sensors for combined processing and transmission.

**Attributes**:
- `data: list[SensorData]`: List of sensor data from different sources (default: None)

**Methods**:

##### `append_data(datum: SensorData)`
- **Purpose**: Adds sensor data from another source
- **Parameters**: `datum` - SensorData object to add

##### `get_full_payload(now) -> str`
- **Purpose**: Creates complete transmission payload with timestamp
- **Parameters**: `now` - datetime object for timestamp
- **Logic**:
  - Formats timestamp as HHMM
  - Concatenates formatted data from all sensors
- **Returns**: Complete payload string (timestamp + all sensor data)

##### `get_csv_format(now) -> list`
- **Purpose**: Formats data for CSV file storage
- **Parameters**: `now` - datetime object for timestamp
- **Logic**:
  - Starts with timestamp
  - Adds all raw datum values from all sensors
- **Returns**: List suitable for CSV writing

### Utility Functions

#### `zeroth_function(zeroes: int, number: str, prefix: bool) -> str`
**Purpose**: Adds zeros to numbers for consistent formatting.

**Parameters**:
- `zeroes: int`: Target total length
- `number: str`: Number string to pad
- `prefix: bool`: If True, add zeros to the left; if False, add to the right

**Logic**:
- Calculates missing zeros needed
- Applies padding based on prefix parameter

**Returns**: Zero-padded string

#### `fill_zeroes(number: float, data_format: _DataFormat) -> str`
**Purpose**: Formats floating-point numbers according to specified data format with zero padding.

**Parameters**:
- `number: float`: The number to format
- `data_format: _DataFormat`: Format specification (e.g., "3.2")

**Logic**:
1. Parses format to get whole and decimal digit requirements
2. Rounds number to required decimal places
3. Splits into whole and decimal parts
4. Handles zero decimal case by clearing decimal string
5. Applies zero padding to both parts
6. Concatenates formatted parts

**Returns**: Formatted string (e.g., "001.30" for input 1.3 with format "3.2")

**Example**:
```python
result = fill_zeroes(1.3, _DataFormat("3.2"))
# Returns: "00130" (note: no decimal point in output)
```

#### `get_null_format(null_format: str, data_format: _DataFormat) -> str`
**Purpose**: Generates null value representation matching the specified data format.

**Parameters**:
- `null_format: str`: Character to use for null representation (typically '#')
- `data_format: _DataFormat`: Format specification (e.g., "3.2")

**Logic**:
1. Parses format to get total digit requirements
2. Creates string with null_format character repeated for total length

**Returns**: Null representation string

**Example**:
```python
result = get_null_format('#', _DataFormat("3.2"))
# Returns: "#####" (5 characters total)
```

### Usage Examples

#### Basic Sensor Data Creation
```python
# Create sensor data for rain gauge
rain_data = SensorData(
    source=DataSource.DIGITAL_RAIN_GAUGE,
    unit='mm',
    date=datetime.now(),
    data=[]
)

# Add measurements
rain_data.append_data(RawData(RAIN_DATA_FORMAT, 12.34))
rain_data.append_data(RawData(RAIN_ACCU_FORMAT, None))  # Missing data

# Get formatted payload
payload = rain_data.get_payload_format()
# Returns: "123400" + null_format_string
```

#### Multi-Sensor Data Compilation
```python
# Combine data from multiple sensors
compiled = CompiledSensorData(data=[rain_data, water_level_data])

# Generate complete payload with timestamp
payload = compiled.get_full_payload(datetime.now())
# Returns: "1425" + rain_data_payload + water_level_payload

# Generate CSV row
csv_row = compiled.get_csv_format(datetime.now())
# Returns: [datetime_obj, 12.34, None, 45.67, ...]
```

### Data Flow
1. **Raw measurements** → `RawData` objects with format specifications
2. **RawData collection** → `SensorData` with metadata and formatting methods
3. **Multi-sensor aggregation** → `CompiledSensorData` for combined processing
4. **Output formatting** → Payload strings for transmission or CSV lists for storage

---

## Module: `generics.py`

### Overview
Provides generic utility functions for CSV file operations, focusing on data writing and efficient retrieval of recent data.

### Purpose
Handles common CSV file operations needed throughout the application, specifically for data logging and retrieval of recent sensor measurements.

### Dependencies
- `csv`: Built-in Python CSV handling library
- `collections.deque`: For efficient last-n-items retrieval

### Functions

#### `write_to_csv(filepath: str, data: list)`
**Purpose**: Appends a new row of data to a CSV file.

**Parameters**:
- `filepath: str`: Path to the target CSV file
- `data: list`: List of values to write as a new row

**Behavior**:
- Opens file in append mode ('a')
- Uses csv.writer for proper CSV formatting
- Writes data as a single row
- Automatically handles file closure

**Use Cases**:
- Logging sensor measurements
- Recording system events
- Appending timestamped data entries

**Example**:
```python
sensor_data = [datetime.now(), 23.5, 45.2, "DRRG"]
write_to_csv("/path/to/data.csv", sensor_data)
```

#### `get_last_n_rows_csv(file_path, n)`
**Purpose**: Efficiently retrieves the last 'n' rows from a CSV file without loading the entire file into memory.

**Parameters**:
- `file_path`: Path to the CSV file to read
- `n`: Number of rows to retrieve from the end of the file

**Algorithm**:
- Uses `collections.deque` with `maxlen=n` for memory-efficient processing
- Streams through the entire file but only retains the last n rows
- Converts deque to list for return value

**Performance Characteristics**:
- **Memory Usage**: O(n) - only stores the last n rows
- **Time Complexity**: O(total_rows) - must read entire file
- **Optimal for**: Cases where n << total_rows

**Returns**: `list` - List of lists, where each inner list represents a row from the last 'n' rows

**Use Cases**:
- Retrieving recent sensor readings for analysis
- Getting latest system status entries
- Fetching recent data for dashboard updates
- Historical data analysis on recent trends

**Example**:
```python
# Get last 10 sensor readings
recent_data = get_last_n_rows_csv("/path/to/sensor_data.csv", 10)
# Returns: [
#   ['2024-01-15 14:30:00', '23.5', '45.2'],
#   ['2024-01-15 14:35:00', '23.7', '45.1'],
#   ...
# ]
```

### Design Considerations

#### Memory Efficiency
- `get_last_n_rows_csv()` uses deque for optimal memory usage when retrieving recent data from large files
- Avoids loading entire CSV into memory, making it suitable for large log files

#### File Safety
- `write_to_csv()` uses context manager ('with' statement) for automatic file closure
- Append mode prevents accidental data loss

#### Error Handling
- Functions don't include explicit error handling
- Will raise standard Python exceptions (FileNotFoundError, PermissionError, etc.)
- Calling code should implement appropriate exception handling

### Usage Patterns

#### Data Logging Workflow
```python
# Continuous data logging
while collecting_data:
    measurements = get_sensor_readings()
    timestamp = datetime.now()
    row_data = [timestamp] + measurements
    write_to_csv(log_file_path, row_data)
```

#### Recent Data Analysis
```python
# Analyze recent trends
recent_readings = get_last_n_rows_csv(log_file_path, 100)
values = [float(row[1]) for row in recent_readings]  # Extract sensor values
average = sum(values) / len(values)
```

### Integration with Project
- Used by main data collection system for sensor data logging
- Supports the project's need for continuous environmental monitoring
- Provides data retrieval for analysis and reporting functions

---

## Module: `logs.py`

### Overview
Manages logging functionality and log file lifecycle for the POSTe-N system, providing event type classification and automatic log file rotation.

### Purpose
Handles system event logging, log file management, and provides automated daily log file rotation to prevent log files from growing indefinitely.

### Dependencies
- `enum`: For event type enumeration
- `datetime`, `timedelta`: For timestamp handling and date calculations  
- `os`: For file system operations
- `configs.parse_string_config`: For reading log file paths from configuration

### Configuration Integration
- `DATA_LOG_PATH`: Retrieved from XML config using `parse_string_config('config.xml', 'datalogpath')`
- `EVENT_LOG_PATH`: Retrieved from XML config using `parse_string_config('config.xml', 'eventlogpath')`

### Enums

#### `EventType`
**Purpose**: Defines categories of system events for logging classification.

**Values**:
- `CMSG_OK = auto()`: Successful confirmed message acknowledgment from LoRa communication
- `CMSG_NOK = auto()`: Failed confirmed message acknowledgment from LoRa communication

**Note**: Comment indicates this enum might be unnecessary (TODO: This enum might be pointless)

**Usage**: 
- Used by `commands.py` for categorizing serial communication events
- Provides standardized event classification for logging and monitoring

### Functions

#### `rename_log_file(now: datetime) -> None`
**Purpose**: Implements daily log file rotation by renaming current log files with previous day's date.

**Parameters**:
- `now: datetime`: Current datetime object used to calculate previous day

**Logic**:
1. Calculates previous day's date using `now - timedelta(days=1)`
2. Formats previous day as "mm-dd-yy" string
3. Renames both data and event log files by inserting date before file extension
4. Uses `os.rename()` for atomic file operations

**File Naming Pattern**:
- **Original**: `data_log.csv`, `event_log.csv`
- **Renamed**: `data_log_01-15-24.csv`, `event_log_01-15-24.csv`

**Example**:
```python
# If called on January 16, 2024
rename_log_file(datetime(2024, 1, 16, 10, 30))
# Renames files to include "01-15-24" (previous day: January 15, 2024)
```

**Use Cases**:
- Daily log rotation triggered by scheduler or main application
- Prevents log files from growing indefinitely
- Maintains historical log files with date-based naming
- Enables log archival and cleanup processes

### Log File Architecture

#### Data Log (`DATA_LOG_PATH`)
- **Purpose**: Stores sensor measurement data and system readings
- **Format**: Typically CSV format for structured data storage
- **Content Examples**: Timestamp, sensor values, device status

#### Event Log (`EVENT_LOG_PATH`)  
- **Purpose**: Records system events, errors, and operational messages
- **Format**: Typically structured logging format
- **Content Examples**: Communication events, error messages, status changes

### Integration Points

#### With Configuration System
```python
# Log paths are dynamically loaded from XML configuration
DATA_LOG_PATH = parse_string_config('config.xml', 'datalogpath')
EVENT_LOG_PATH = parse_string_config('config.xml', 'eventlogpath')
```

#### With Command System
```python
# EventType used in commands.py for event classification
from logs import EventType
CMSG_AWK_REPLY_OK = ReplyFormat('ACK Received', 'Done', EventType.CMSG_OK)
```

### Log Rotation Strategy

#### Daily Rotation
- **Trigger**: Application calls `rename_log_file()` at midnight or startup
- **Retention**: Renamed files remain until manual cleanup
- **Benefits**: 
  - Prevents single large log files
  - Enables date-based log analysis
  - Facilitates log archiving and backup

#### File Naming Convention
```
Original:  data_log.csv
Rotated:   data_log_mm-dd-yy.csv

Examples:
data_log_01-15-24.csv  (January 15, 2024)
event_log_12-31-23.csv (December 31, 2023)
```

### Error Considerations
- **File Operations**: `os.rename()` may raise OSError if files are locked or permissions insufficient
- **Missing Files**: Will raise FileNotFoundError if log files don't exist
- **Path Issues**: Depends on valid paths from configuration file

### Usage Example
```python
from datetime import datetime
from logs import rename_log_file, EventType

# Daily log rotation (typically called at midnight)
current_time = datetime.now()
rename_log_file(current_time)

# Event classification in communication handling
if message_acknowledged:
    event_type = EventType.CMSG_OK
else:
    event_type = EventType.CMSG_NOK
```

### Future Improvements
Based on TODO comments:
- Consider removing `EventType` enum if not providing sufficient value
- Add error handling for file operations
- Implement configurable retention policies
- Add log compression for archived files

---

## Summary

The POSTe-N system consists of six main Python modules that work together to provide environmental monitoring and data transmission capabilities:

1. **commands.py** - LoRa communication and AT command handling  
2. **configs.py** - XML configuration parsing and serial parameter management
3. **data.py** - Sensor data structures and payload formatting
4. **generics.py** - CSV utility functions for data persistence
5. **logs.py** - Logging system and file rotation management

Each module is designed with specific responsibilities and clean interfaces, following object-oriented and functional programming principles where appropriate. The system supports digital rain gauges (DRRG) and digital staff gauges (DSG) for environmental monitoring with LoRa wireless transmission capabilities.