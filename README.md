# Ping Sweep Script

This Python script performs a ping sweep on a list of subnets and stores the results in CSV files. It can be used to compare the results of pre- and post-change network conditions.

## Features

- Ping sweep on a list of subnets
- Store results in CSV files
- Compare pre- and post-change results
- Customizable timeout for pings
- Option to specify custom filenames for comparison results
- Includes timestamp for each ping

## Requirements

- Python 3.6 or higher

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/samlama1/ping-sweep.git
   cd ping-sweep
   ```

2. Ensure you have Python 3.6 or higher installed.

## Usage

### Pre-Sweep

Run the pre-sweep to collect initial ping results:

```sh
python ping_sweep.py pre subnets.txt
```

### Post-Sweep

Run the post-sweep to collect ping results after changes:

```sh
python ping_sweep.py post subnets.txt
```

### Comparison

Compare the pre- and post-sweep results and store the comparison in a custom file:

```sh
python ping_sweep.py post subnets.txt --compare comparison_results.csv
```

### Arguments

- `mode`: `pre` for pre-sweep, `post` for post-sweep
- `filename`: Filename containing the list of subnets
- `--timeout`: Timeout for each ping in milliseconds (default: 100ms)
- `--compare`: Compare results with pre-sweep and store in the specified file (default: `ping_sweep_comparison_results.csv`)

### Example

1. Create a file named `subnets.txt` with the following content:

   ```
   192.168.1.0/24
   10.0.0.1
   ```

2. Run the pre-sweep:

   ```sh
   python ping_sweep.py pre subnets.txt --timeout 50
   ```

3. Make changes to your network.

4. Run the post-sweep and compare the results:

   ```sh
   python ping_sweep.py post subnets.txt --timeout 50 --compare custom_comparison_results.csv
   ```

## Output

- `ping_sweep_pre_results.csv`: Results of the pre-sweep
- `ping_sweep_post_results.csv`: Results of the post-sweep
- `custom_comparison_results.csv`: Comparison of pre- and post-sweep results (if `--compare` is specified)
