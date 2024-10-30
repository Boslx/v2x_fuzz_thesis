import matplotlib.pyplot as plt

from scapy.all import Ether, rdpcap

from fields.Etsi_Its_Msgs import *


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
            self.generation_time_history.append(generation_delta_time_delta)

    def show_packets(self, pcap_file_path):
        packets = rdpcap(pcap_file_path)
        for packet_pcap in packets:
            self.handle_packet(packet_pcap)

        return self.generation_time_history


def plot_data(data1, data2):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6, 3))

    ax1.scatter(range(len(data1)), data1, s=2)
    ax1.set_title('ID.3 stationary')
    ax1.set_xlabel('CAM message interval index')
    ax1.set_ylabel('CAM time interval in ms')

    ax2.scatter(range(len(data2)), data2, s=2)
    ax2.set_title('ID.3 suburban')
    ax2.set_xlabel('CAM message interval index')
    #ax2.set_ylabel('CAM time interval in ms')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    pcap_file_path1 = r"D:\Projects\v2x-fuzz-thesis\experiments\BlackBoxFuzzing\testDrive\CAMstehend.pcapng"
    pcap_file_path2 = r"D:\Projects\v2x-fuzz-thesis\experiments\BlackBoxFuzzing\testDrive\BundesstraßeAuto.pcapng"

    intervalHist1 = PacketHandler()
    data1 = intervalHist1.show_packets(pcap_file_path1)

    intervalHist2 = PacketHandler()
    data2 = intervalHist2.show_packets(pcap_file_path2)

    plot_data(data1, data2)
