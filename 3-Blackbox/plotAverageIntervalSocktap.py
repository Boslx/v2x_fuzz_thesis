import argparse
from datetime import datetime, timezone
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
from scapy_etsi_its.Etsi_Its_Msgs import *


def coord_to_double(integer_value):
    return integer_value / 1e7


def calculate_time_difference(start_time, end_time):
    if end_time >= start_time:
        return end_time - start_time
    return 65535 - start_time + end_time


class PacketHandler:
    def __init__(self):
        self.generation_time_history = []
        self.last_generation_time = None

    def calc_generation_time_delta(self, generation_time):
        if self.last_generation_time is not None:
            result = calculate_time_difference(self.last_generation_time, generation_time)
            self.last_generation_time = generation_time
            return result
        self.last_generation_time = generation_time
        return None

    def handle_packet(self, dissected):
        if not isinstance(dissected, Ether):
            return
        if GeoBasicHeader not in dissected:
            logging.info("Received message is not C-ITS, skipping")
            return
        if ITS_CAM not in dissected:
            logging.info("Received message is not CAM, skipping")
            return

        print(dissected.show(dump=True))

        timestamp = dissected[SingleHopBroadcast].timestamp
        debug = dissected[ITS_CAM].asn1.get_val()
        generation_delta_time = dissected[ITS_CAM].asn1.get_val_at(['cam', 'generationDeltaTime'])
        generation_delta_time_delta = self.calc_generation_time_delta(generation_delta_time)

        speed = dissected[ITS_CAM].asn1.get_val_at(['cam', 'camParameters', 'highFrequencyContainer',
                                                    'basicVehicleContainerHighFrequency', 'speed', 'speedValue'])

        latitude = dissected[SingleHopBroadcast].latitude
        longitude = dissected[SingleHopBroadcast].longitude

        if generation_delta_time_delta is not None:
            if generation_delta_time_delta < 1200:
                self.generation_time_history.append(generation_delta_time_delta)

    def show_packets(self, pcap_file_path):
        packets = rdpcap(pcap_file_path)
        for packet_pcap in packets:
            self.handle_packet(packet_pcap)

        return self.generation_time_history

        # Create histogram
        plt.hist(data, bins=10, edgecolor='black', range=[997, 1007], weights=np.ones(len(data)) / len(data))

        # Add titles and labels
        plt.title('Histogram of Socktab CAM Messages')
        plt.xlabel('Interval length')
        plt.ylabel('Frequency')
        plt.gca().yaxis.set_major_formatter(PercentFormatter(1))

        # Show plot
        plt.show()


if __name__ == "__main__":
    pcap_file_path = r"/BlackBoxFuzzing/testDrive/SocktapCohdaWireless.pcapng"

    fuzzer = PacketHandler()
    data_good = fuzzer.show_packets(pcap_file_path)

    interval_file_path = r"/BlackBoxFuzzing/testDrive/fuzzedIntervals.txt"
    with open(interval_file_path, 'r') as file:
        # Read each line, strip newline characters, and convert to integer
        data_bad = [int(line.strip()) for line in file]

    bins = np.linspace(950, 1300, 35)

    fig, ax = plt.subplots(figsize=(5, 3.5))

    # Create histogram for data_good
    ax.hist(data_good, bins=bins, edgecolor='black', weights=np.ones(len(data_good)) / len(data_good), alpha=0.5,
            label='Normal')
    # Create histogram for data_bad
    ax.hist(data_bad, bins=bins, edgecolor='black', weights=np.ones(len(data_bad)) / len(data_bad), alpha=0.5,
            label='Crashed')

    # Add titles and labels
    ax.set_xlabel('Measured CAM time interval in ms')
    ax.grid(True, color="grey", linewidth="0.4", linestyle="-.")
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.legend()

    # Adjust layout
    fig.tight_layout()

    # Show plot
    plt.show()
