# Measurement tool
Configure in main.py file. Any Python expression may be used.

## ARGS
In any place, where quick changing of parameters is desired, command line arguments might be used instead of fixed configuration.
When program is run with:

python main.py ABC DEF

then ARGS[1] = "ABC" and ARGS[2] = "DEF"

## CONN_PARAMS
This parameter contains data required to connect to thrust stand and microphone.
- nor_addr - microphone IP address
- nor_ftp_user - micropphone FTP username
- nor_ftp_pass - microphone FTP password
- nor_recordings_dir - microphone recorded data path
- stand_tty - serial port, trust stand is attached to, COM... for windows, /dev/tty... for linux

## PWM_RANGE
Sets the sequence of throttle levels, that will be included in measurement.
Use any Python that will evaluate to Iterable[int].

Examples:
- PWM_RANGE = range(1100, 2000, 100) - 1000, 1100, ..., 1800, 1900 - range from 1100 to 2000 with step of 100. Note it does NOT include the end value.
- PWM_RANGE = list(range(1100, 1500, 50)) + list(range(1500, 2000, 50)) - 1000, 1100, 1200, 1300, 1400,   1500, 1550, ..., 1900, 1950. - Ranges may be joined to achieve not uniform distribution.
- PWM_RANGE = [1300, 1800, 1900, 1950, 1975, 1990, 2000] - Fully custom measurement may be defined by specifying list of throttle levels manually.


## OUTPUT_FILE
This parameter specifies name of the directory, that will be created and written with measurement series data.
Convenient to use with ARGS.

Examples:
- OUTPUT_FILE = 'tests/baseline_r1_a0' - measurement will be saved to specified directory
- OUTPUT_FILE = ARGS[1] - first argument will be used as output name. Run program with 'python main.py tests/baseline_r1_a0' to achieve the same effect as above


# Data visualizer

Run with:
python visualizer.py [list of measurement series to visualize]

Examples:
- python visualizer.py tests/baseline_r1_a0 tests/baseline_r1_a90 - plots these two series
- python visualizer.py tests/* - plots all series in 'tests' directory
- python visualizer.py tests/baseline_r*_a0 - plots all series matching the expression - baseline_r1_a0, baseline_r2_a0, etc.
