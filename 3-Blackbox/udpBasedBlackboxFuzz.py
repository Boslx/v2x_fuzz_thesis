import argparse
from datetime import datetime, timezone

from scapy.all import Ether

from scapy_etsi_its.Etsi_Its_Msgs import *


class PacketHandlingResult(Enum):
    SKIPPED = 0
    OKAY = 1
    ABNORMAL = 2
    NOT_RESPONDING = 3
    PROBABLY_OKAY = 999


def coord_to_double(integer_value):
    return integer_value / 1e7


def calculate_time_difference(start_time, end_time):
    if end_time >= start_time:
        return end_time - start_time
    return 65535 - start_time + end_time


def elapsed_tai_milliseconds():
    reference_time = datetime(2004, 1, 1, tzinfo=timezone.utc)
    current_time = datetime.now(timezone.utc)

    # Calculate the number of elapsed TAI milliseconds since the reference time
    tst_tai_ms = int((current_time - reference_time).total_seconds() * 1000) + current_time.microsecond

    # Calculate the TST value
    return tst_tai_ms % (2 ** 32)

def bitflip_fuzzer(data, intensity=0.1):
    """
    Bitflip fuzzer that flips bits in the input data.

    Parameters:
    data (bytes): The input data to fuzz.
    intensity (float): The intensity of bitflipping (0.0 to 1.0).

    Returns:
    bytes: The fuzzed data.
    """

    return bytes(data)

    if not (0.0 <= intensity <= 1.0):
        raise ValueError("Intensity must be between 0.0 and 1.0")

    num_bits = len(data) * 8
    num_flips = int(num_bits * intensity)

    bit_positions = random.sample(range(num_bits), num_flips)

    fuzzed_data = bytearray(data)

    for bit_pos in bit_positions:
        byte_index = bit_pos // 8
        bit_index = bit_pos % 8
        fuzzed_data[byte_index] ^= 1 << bit_index

    return bytes(fuzzed_data)


def get_seeds(folder_path):
    crazy_level = 0.0

    while True:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.getsize(file_path) > 1600:
                    continue
                with open(file_path, "rb") as file_bin:
                    yield bitflip_fuzzer(file_bin.read(), crazy_level)

        crazy_level = (crazy_level + 0.02) % 1


class PacketHandler:
    def __init__(self, output_dir, seed_folder, packet_interval, high_threshold, low_threshold):
        self.position_watched = None
        self.generation_time_history = collections.deque(maxlen=100)
        self.last_generation_time = None
        self.found_anomalies = 0
        self.seed_history = []
        self.output_dir = output_dir
        self.seed_folder = seed_folder
        self.packet_interval = packet_interval
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold
        self.speed = 0
        self.latitude = 488251815
        self.longitude = 90960904
        self.classic = False

    def calc_generation_time_delta(self, generation_time):
        if self.last_generation_time is not None:
            result = calculate_time_difference(self.last_generation_time, generation_time)
            self.last_generation_time = generation_time
            return result
        self.last_generation_time = generation_time
        return None

    def write_anomalies(self):
        file_path = os.path.join(self.output_dir, f"out_{self.found_anomalies}")
        os.makedirs(file_path, exist_ok=True)

        for i, byte_data in enumerate(self.seed_history):
            file_name = f"{file_path}/seed_{i}_speed_{self.speed}.bin"
            with open(file_name, "wb") as file:
                file.write(byte_data)

        self.found_anomalies += 1
        self.seed_history.clear()

    def handle_packet(self, dissected) -> PacketHandlingResult:
        if not isinstance(dissected, Ether):
            return PacketHandlingResult.SKIPPED
        if GeoBasicHeader not in dissected:
            logging.info("Received message is not C-ITS, skipping")
            return PacketHandlingResult.SKIPPED
        if ITS_CAM not in dissected:
            logging.info("Received message is not CAM, skipping")
            return PacketHandlingResult.SKIPPED

        generation_delta_time = dissected[ITS_CAM].asn1.get_val_at(['cam', 'generationDeltaTime'])
        generation_delta_time_delta = self.calc_generation_time_delta(generation_delta_time)

        self.speed = dissected[ITS_CAM].asn1.get_val_at(['cam', 'camParameters', 'highFrequencyContainer',
                                                    'basicVehicleContainerHighFrequency', 'speed', 'speedValue'])

        self.latitude = dissected[SingleHopBroadcast].latitude
        self.longitude = dissected[SingleHopBroadcast].longitude

        if generation_delta_time_delta is not None:
            self.generation_time_history.append(generation_delta_time_delta)

        if generation_delta_time_delta is None:
            return PacketHandlingResult.PROBABLY_OKAY

        if self.classic:
            if generation_delta_time_delta > self.high_threshold:
                logging.info(f"interval of {generation_delta_time_delta} - unusual high generation time interval deviation!")
                return PacketHandlingResult.ABNORMAL
            elif generation_delta_time_delta < self.low_threshold:
                logging.info(f"interval of {generation_delta_time_delta} - unusual low generation time interval deviation!")
                return PacketHandlingResult.ABNORMAL
            else:
                logging.info(f"interval of {generation_delta_time_delta} ms with a speed of {self.speed}")
                return PacketHandlingResult.OKAY
        else:
            generation_delta_time_delta = generation_delta_time_delta
            diff_interesting = generation_delta_time_delta % 100
            if diff_interesting > 50:
                diff_interesting = 100 - diff_interesting

            if diff_interesting > 10:
                logging.info(f"interval of {generation_delta_time_delta} - unusual high generation time interval deviation!")
                return PacketHandlingResult.ABNORMAL
            else:
                logging.info(f"interval of {generation_delta_time_delta} ms with a speed of {self.speed}")
                return PacketHandlingResult.OKAY

    def packet_handler(self, packet):
        handle = self.handle_packet(packet)
        if handle == PacketHandlingResult.ABNORMAL:
            self.write_anomalies()

    def show_packets(self):
        for index, seed in enumerate(get_seeds(self.seed_folder)):
            # to_send = Ether(dst='ff:ff:ff:ff:ff:ff', src='00:e0:4c:68:8d:cd', type=35143) / Raw(load=bytes(seed))
            to_send = (Ether(dst='ff:ff:ff:ff:ff:ff', src='00:e0:4c:68:8d:cd', type=35143)
                       / GeoBasicHeader(Version=1, NH=1, Reserved=0, LT=26, RHL=10)
                       / GeoCommonHeader(NH=2, Reserved1=0, HT=4, HST=0, TC=3, Flags=0, PL=104, MHL=10, Reserved2=0)
                       / GeoBroadcast(sequence_number=1 + index, reserved1=0, manual=0, HT=15, reserved2=0,
                                      address=56926285176, timestamp=elapsed_tai_milliseconds(), latitude=self.latitude,
                                      longitude=self.longitude, position_accuracy=1, speed=1, heading=3109,
                                      geo_area_position_latitude=self.latitude, geo_area_position_longitude=self.longitude,
                                      distance_a=400, distance_b=0, angle=0, reserved3=0)
                       / BTPB(dport=2003, dport_info=2003)
                       / Raw(load=bytes(seed)))

            sendp(to_send, iface="enx00e04c688dcd", verbose=False)
            self.seed_history.append(seed)

            if index % self.packet_interval == 0:
                sniff(count=1, filter="ether dst ff:ff:ff:ff:ff:ff", prn=self.packet_handler, iface="enx00e04c688dcd")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Packet Handler Configuration")
    parser.add_argument("-o", "--output", type=str, required=True, help="Output directory for anomalies")
    parser.add_argument("-i", "--input", type=str, required=True, help="Folder containing seed files")
    parser.add_argument("--packet_interval", type=int, default=3, help="Packet interval for sniffing")
    parser.add_argument("-hi", "--high_threshold", type=int, default=1100,
                        help="High threshold for generation time interval")
    parser.add_argument("-lo", "--low_threshold", type=int, default=990,
                        help="Low threshold for generation time interval")

    args = parser.parse_args()

    logging.getLogger().setLevel(logging.INFO)
    fuzzer = PacketHandler(args.output, args.input, args.packet_interval, args.high_threshold,
                           args.low_threshold)
    fuzzer.show_packets()
