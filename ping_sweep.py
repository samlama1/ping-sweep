import subprocess
import csv
import ipaddress
import sys
import concurrent.futures
import time
import platform
import argparse
from datetime import datetime

def ping_ip(ip, timeout):
    try:
        start_time = time.time()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if platform.system().lower() == 'windows':
            # Windows ping command
            output = subprocess.check_output(['ping', '-n', '1', '-w', str(timeout), str(ip)], stderr=subprocess.STDOUT, universal_newlines=True)
        else:
            # Unix-based ping command
            output = subprocess.check_output(['ping', '-c', '1', '-W', str(timeout // 1000), str(ip)], stderr=subprocess.STDOUT, universal_newlines=True)
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        if '1 received' in output or '1 packets received' in output:
            result = (timestamp, str(ip), 'Reachable', response_time)
        else:
            result = (timestamp, str(ip), 'Unreachable', None)
    except subprocess.CalledProcessError:
        result = (timestamp, str(ip), 'Unreachable', None)
    except Exception as e:
        result = (timestamp, str(ip), 'Error', None)
        print(f"Error pinging {ip}: {e}")
    
    print(f"Pinged {ip} at {timestamp}: {result[2]} with response time {result[3] if result[3] is not None else 'N/A'} ms")
    return result

def ping_sweep(subnets, timeout):
    results = []
    for subnet in subnets:
        print(f"Starting ping sweep for subnet: {subnet}")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_ip = {executor.submit(ping_ip, ip, timeout): ip for ip in ipaddress.IPv4Network(subnet)}
            for future in concurrent.futures.as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as exc:
                    print(f'{ip} generated an exception: {exc}')
        print(f"Completed ping sweep for subnet: {subnet}")
    return results

def write_csv(filename, data):
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'IP Address', 'Status', 'Response Time (ms)'])
            writer.writerows(data)
    except Exception as e:
        print(f"Error writing to CSV file {filename}: {e}")

def read_subnets(filename):
    subnets = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if '/' not in line:
                    # No subnet mask provided, assume /32
                    line += '/32'
                try:
                    # Validate and add the subnet
                    subnets.append(str(ipaddress.IPv4Network(line, strict=False)))
                except ValueError:
                    print(f"Invalid subnet: {line}. Skipping.")
    except Exception as e:
        print(f"Error reading subnets from file {filename}: {e}")
    return subnets

def compare_results(pre_results, post_results):
    comparison = []
    pre_dict = {ip: (timestamp, status, response_time) for timestamp, ip, status, response_time in pre_results}
    post_dict = {ip: (timestamp, status, response_time) for timestamp, ip, status, response_time in post_results}

    for ip in pre_dict:
        pre_timestamp, pre_status, pre_response_time = pre_dict[ip]
        post_timestamp, post_status, post_response_time = post_dict.get(ip, (None, 'Not in post-sweep', None))
        if pre_status == 'Reachable' and post_status == 'Unreachable':
            comparison.append((pre_timestamp, ip, 'Was reachable, now unreachable', pre_response_time, post_response_time, pre_response_time))
        elif pre_status == 'Unreachable' and post_status == 'Reachable':
            comparison.append((pre_timestamp, ip, 'Was unreachable, now reachable', pre_response_time, post_response_time, post_response_time))
        elif pre_status == post_status:
            latency_difference = (post_response_time - pre_response_time) if pre_response_time and post_response_time else None
            comparison.append((pre_timestamp, ip, f'Still {pre_status.lower()}', pre_response_time, post_response_time, latency_difference))
        else:
            comparison.append((pre_timestamp, ip, 'Status changed', pre_response_time, post_response_time, None))

    return comparison

def write_comparison_csv(filename, data):
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'IP Address', 'Status Change', 'Pre Response Time (ms)', 'Post Response Time (ms)', 'Latency Difference (ms)'])
            writer.writerows(data)
    except Exception as e:
        print(f"Error writing to comparison CSV file {filename}: {e}")

def main():
    try:
        parser = argparse.ArgumentParser(description="Ping sweep script")
        parser.add_argument('mode', choices=['pre', 'post'], help="Mode: 'pre' for pre-sweep, 'post' for post-sweep")
        parser.add_argument('filename', help="Filename containing the list of subnets")
        parser.add_argument('--timeout', type=int, default=100, help="Timeout for each ping in milliseconds (default: 100ms)")
        parser.add_argument('--compare', nargs='?', const='ping_sweep_comparison_results.csv', help="Compare results with pre-sweep and store in the specified file (default: ping_sweep_comparison_results.csv)")
        args = parser.parse_args()

        mode = args.mode
        filename = args.filename
        timeout = args.timeout  # Timeout in milliseconds
        compare_filename = args.compare

        subnets = read_subnets(filename)
        if not subnets:
            print("No valid subnets to process. Exiting.")
            return

        results = ping_sweep(subnets, timeout)

        if mode == 'pre':
            write_csv('ping_sweep_pre_results.csv', results)
        elif mode == 'post':
            write_csv('ping_sweep_post_results.csv', results)
            if compare_filename:
                pre_results = []
                try:
                    with open('ping_sweep_pre_results.csv', 'r') as pre_file:
                        reader = csv.reader(pre_file)
                        next(reader)  # Skip header
                        pre_results = [(row[0], row[1], row[2], float(row[3]) if row[3] and row[3] != 'None' else None) for row in reader]
                except Exception as e:
                    print(f"Error reading pre-sweep results: {e}")
                    return

                comparison = compare_results(pre_results, results)
                write_comparison_csv(compare_filename, comparison)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
