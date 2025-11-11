"""
This script analyzes a profiling text file for Astra SL1600 NPU (Neural Processing Unit) layers,
counts the number of layers by type (NN, TP, SH), and reports the top layers by cycle and execution time.

When a model is converted on Host, use the following commands:
synap convert --model model.tflite --target SL1680 --meta tf.yaml --out-dir out --profiling

It creates a model.synap file which is profiling model for Astra SL1600 NPU.
Infer the model using
synap_cli -m model.synap --profiling tf.txt -r 5 random

This generates a profiling txt file that can be analyzed using this script.
It expects a specific profiling txt file as input file and outputs summary statistics for layer performance.
"""

import sys
import re

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 synap_profiling_npu.py <txt_file>")
        sys.exit(1)
    txt_file = sys.argv[1]
    layer_counts = {'NN': 0, 'TP': 0, 'SH': 0}
    layer_times = []
    layer_details = []
    try:
        with open(txt_file) as f:
            for line in f:
                m = re.match(r'\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|.*\|\s*(NN|TP|SH)\s*\|\s*([^\|]+)', line)
                if m:
                    lyr, cycle, time_us, ot, name = int(m.group(1)), int(m.group(2)), int(m.group(3)), m.group(4), m.group(5).strip()
                    if ot in layer_counts:
                        layer_counts[ot] += 1
                    layer_times.append((cycle, name))
                    layer_details.append((cycle, name, ot, time_us))
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    if not layer_details:
        print("No valid layer data found in file.")
        sys.exit(1)
    print("Layer counts by OT type:")
    for ot, count in layer_counts.items():
        print(f"{ot}: {count}")
    print(f"Total layers counted: {sum(layer_counts.values())}")
    # Top 1 layer by cycle
    top_layer = max(layer_times, key=lambda x: x[0])
    print(f"Top 1 layer by cycle: {top_layer[1]} (cycle: {top_layer[0]})")
    # Top 10 layers by cycle
    top_10_layers = sorted(layer_details, key=lambda x: x[0], reverse=True)[:10]
    print("Top 10 layers by cycle (with OT type and time_us):")
    for i, (cycle, name, ot, time_us) in enumerate(top_10_layers, 1):
        print(f"{i}. {name} | OT: {ot} | cycle: {cycle} | time_us: {time_us}")

if __name__ == "__main__":
    main()
