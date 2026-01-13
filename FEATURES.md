# ARS Noise Measurement System - Features Documentation

## Overview

This is an automated measurement system designed for drone/UAV propulsion testing. It integrates a **thrust stand** with a **Norsonic sound level meter** to simultaneously capture mechanical and acoustic performance data across various throttle (PWM) settings.

---

## Core Features

### 1. Automated Measurement Orchestration (`measurement_station.py`, `measure.py`)

- **Coordinated multi-device measurement**: Simultaneously controls thrust stand and Norsonic microphone
- **PWM sweep automation**: Automatically cycles through configurable throttle levels
- **RPM stabilization**: Waits for motor RPM to stabilize before capturing data (`stabilize_rpm()` with configurable window and tolerance)
- **Tare/zeroing**: Automatic tare of thrust, torque, and current sensors before measurement
- **Graceful motor shutdown**: Gradually reduces PWM (10 PWM per 100ms) to prevent sudden stops
- **Data persistence**: Saves measurement series as pickled Python objects

### 2. Thrust Stand Control (`thrust_stand.py`, `msp.py`)

- **MSP protocol communication**: Custom MSP (Multiwii Serial Protocol) implementation for RCBenchmark-style stands
- **Real-time data acquisition**:
  - Thrust force (with calibration constants)
  - Torque (calculated from dual load cells with hinge geometry)
  - Rotational speed (electrical and optical RPM)
  - ESC voltage, current, and power
  - Temperature sensors (3 channels)
  - Accelerometer data (X, Y, Z)
  - Vibration measurement
  - Pressure readings
- **Calibration support**: Configurable calibration constants for:
  - Motor pole count
  - Load cell calibration factors
  - Hinge distances for torque calculation
- **Asynchronous polling**: ~30ms polling interval with async I/O
- **Measurement series**: Start/stop measurement series with sample tracking

### 3. Norsonic Sound Level Meter Integration (`norsonic.py`, `norsonic_fetcher.py`, `norsonic_parser.py`)

- **WebSocket control**: Real-time control via WebSocket connection (`ws://[IP]/live`)
- **Automated recording workflow**:
  - Initialize new measurement
  - Start recording
  - Wait for completion
  - Retrieve filename
- **FTP data retrieval**: Fetches recorded measurements via FTP with:
  - Custom FTP line parser for Norsonic directory format
  - Automatic reconnection on connection reset
  - Support for batch downloads
- **Report parsing**:
  - Profile data (time-series measurements)
  - Global functions (aggregate metrics)
  - FFT spectrum data (up to ~22kHz)

### 4. FFT Analysis (`fft.py`)

- **FFT data container**: Frequency-domain data with arithmetic operations
- **Interpolable operations**:
  - Addition of FFT datasets
  - Scalar multiplication
- **Key-based interpolation**: For comparing FFT data at non-measured operating points

### 5. Data Visualization (`visualizer.py`)

- **Bokeh-based interactive visualization server**:
  - Multi-series comparison
  - Configurable X and Y axes from any measured parameter
  - Source selection for comparing multiple measurement series
  - Auto-scaling Y-axis with margins
- **FFT visualization**:
  - Interactive FFT plot
  - Interpolated FFT at custom operating points
- **Glob pattern support**: Load multiple measurement files using shell wildcards

### 6. Dash Web Application (`dash/`)

#### 6.1 Capture Tab (`dash/capture.py`)
- **Measurement configuration UI**:
  - PWM values input with validation
  - Metadata fields (Description, Motor, Prop)
- **Live measurement log**: Real-time logging during capture
- **Start/stop controls**

#### 6.2 Browse Tab (`dash/db_browser.py`)
- **Database browser**: Filter and browse saved measurements
- **Multi-attribute filtering**: Filter by Motor, Prop, Description, Shroud
- **Comparison selection**: Checkbox-based selection for multi-series comparison
- **Integration with visualizer**: Selected measurements auto-load in analyzer

#### 6.3 Analyze Tab (`dash/main.py`)
- **Embedded visualizer**: iFrame integration with Bokeh visualizer
- **Dynamic URL generation**: Passes selected files to visualizer via URL parameters

### 7. Mathematical Utilities (`interpolation.py`)

- **Linear interpolation**: Generic interpolation for any `Interpolable` type
- **Binary search**: Efficient argument finding in sorted sequences
- **Keyed interpolation**: Interpolate between data points based on any measurable property

### 8. Async Serial Communication (`async_serial.py`)

- **Async serial wrapper**: Converts blocking `pyserial` to asyncio-compatible streams
- **Custom transport**: Implements `asyncio.Transport` for serial ports
- **Event-driven reading**: Uses event loop file descriptor monitoring

### 9. Logging System (`logger.py`)

- **Timestamped console output**: Colored output with millisecond precision
- **File logging**: Automatic log file creation with datetime naming
- **Prefix support**: Create prefixed loggers for module-specific output

---

## Configuration Options (`main.py`)

| Parameter | Description | Example |
|-----------|-------------|---------|
| `stand_tty` | Serial port for thrust stand | `/dev/ttyUSB0`, `COM7` |
| `nor_addr` | Norsonic microphone IP | `10.145.1.1` |
| `nor_ftp_user` | FTP username | `AAAA` |
| `nor_ftp_pass` | FTP password | `1234` |
| `nor_recordings_dir` | Recording storage path | `/SD Card/NorMeas/...` |
| `PWM_RANGE` | Throttle levels to test | `range(1100, 1800, 100)` |
| `OUTPUT_FILE` | Output directory name | `tests/baseline_r1_a0` |

---

## Data Structures

### OpPointData
Represents a single operating point measurement:
- `data_thrust_stand`: Sequence of thrust stand samples
- `raw_nor_report`: Raw Norsonic report data
- `pwm_setpoint`: PWM value for this operating point
- Properties: `nor_report_parsed`, `data_accustic`, `data_thrust_stand_avg`, `data_accustic_avg`, `data_fft`

### ThrustStandMeasurement
Single thrust stand sample:
- `thrust`: Force in Newtons
- `torque`: Torque in Nm
- `rot_speed`: RPM
- `volt`: ESC voltage
- `current`: ESC current

### NorsonicReportData
Parsed acoustic measurement:
- `profile`: Time-series data
- `glob_funcs`: Aggregate functions
- `glob_fft`: Frequency spectrum

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `pyserial` | Serial communication with thrust stand |
| `websockets` | Norsonic WebSocket control |
| `aioftp` | FTP file retrieval from Norsonic |
| `aiohttp` | Async HTTP support |
| `bokeh` | Interactive visualization |
| `dash` + `dash-bootstrap-components` | Web dashboard UI |
| `scipy` | Scientific computing |
| `matplotlib` | Plotting |
| `colorist` | Colored console output |

---

## Usage

### Running a Measurement
```bash
python main.py [output_directory]
# Example: python main.py tests/motor_test_1
```

### Visualizing Results
```bash
python visualizer.py [measurement_directories...]
# Examples:
python visualizer.py tests/baseline_r1_a0 tests/baseline_r1_a90
python visualizer.py tests/*
python visualizer.py tests/baseline_r*_a0
```

### Running the Dashboard
```bash
cd dash
python main.py
# Navigate to http://127.0.0.1:8050
```

---

## Architecture

```
┌─────────────────┐     Serial/MSP      ┌─────────────────┐
│   main.py       │◄───────────────────►│  Thrust Stand   │
│  (orchestrator) │                     │  (RCBenchmark)  │
└────────┬────────┘                     └─────────────────┘
         │
         │ async
         ▼
┌─────────────────┐     WebSocket       ┌─────────────────┐
│ measurement_    │◄───────────────────►│    Norsonic     │
│ station.py      │                     │  Sound Meter    │
└────────┬────────┘         FTP         └─────────────────┘
         │                   │
         │                   │
         ▼                   ▼
┌─────────────────────────────────────────────────────────┐
│                    pickle file                          │
│              (measurement data store)                   │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
         ┌──────────────────┴──────────────────┐
         │                                     │
         ▼                                     ▼
┌─────────────────┐                   ┌─────────────────┐
│  visualizer.py  │                   │   dash/main.py  │
│  (Bokeh server) │                   │  (Web dashboard)│
└─────────────────┘                   └─────────────────┘
```

---

## Hardware Requirements

- **Thrust Stand**: RCBenchmark-compatible with MSP protocol support
- **Sound Level Meter**: Norsonic with WebSocket API and FTP access
- **Serial Interface**: USB-to-Serial adapter for thrust stand
- **Network**: Ethernet/WiFi connection to Norsonic device

---

## File Structure

```
ars_noise_measurement/
├── main.py                 # Entry point and configuration
├── measure.py              # Measurement execution wrapper
├── measurement_station.py  # Orchestration and data structures
├── thrust_stand.py         # Thrust stand control
├── msp.py                  # MSP protocol implementation
├── async_serial.py         # Async serial wrapper
├── norsonic.py             # Norsonic WebSocket control
├── norsonic_fetcher.py     # FTP data retrieval
├── norsonic_parser.py      # Report parsing
├── fft.py                  # FFT data structures
├── interpolation.py        # Math utilities
├── visualizer.py           # Bokeh visualization server
├── logger.py               # Logging utilities
├── db.py                   # Database structures (WIP)
├── dash/                   # Web dashboard
│   ├── main.py             # Dash application
│   ├── capture.py          # Capture tab component
│   └── db_browser.py       # Database browser component
├── Pipfile                 # Python dependencies
└── README.txt              # Original documentation
```
