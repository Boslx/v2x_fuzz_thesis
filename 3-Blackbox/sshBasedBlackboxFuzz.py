import argparse
import collections
import logging

import paramiko
from geopy.distance import geodesic
from scapy.layers.dot11 import Dot11, Dot11QoS
from enum import Enum

from scapy.layers.l2 import LLC

from scapy_etsi_its.Etsi_Its_Msgs import *

udp_device_ip = "239.118.122.97"
udp_device_port = 8947
input_dir = "C:\\Users\\lbosch\\Desktop\\tmp\\sub_5_routerIndi\\queue"
output_dir = "D:\\output_fuz"
num_samples_before_check = 12


class TargetNotResponding(Exception):
    pass


def coord_to_double(integer_value):
    return integer_value / 1e7


def calculate_time_difference(start_time, end_time):
    # Calculate the time difference considering the circular nature of the timestamps
    if end_time >= start_time:
        time_difference = end_time - start_time
    else:
        time_difference = 65535 - start_time + end_time

    return time_difference


def get_seeds(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            if size > 2304:
                continue
            with open(file_path, "rb") as file_bin:
                file_bytes = file_bin.read()
                yield bytes(file_bytes)


class PacketHandlingResult(Enum):
    SKIPPED = 0
    OKAY = 1
    ABNORMAL = 2
    NOT_RESPONDING = 3
    PROBABLY_OKAY = 999


class PacketHandler:
    position_watched = None

    generation_time_history = collections.deque(maxlen=100)

    last_generation_time = None

    def calc_generation_time_delta(self, generation_time):
        result = None
        if self.last_generation_time is not None:
            result = calculate_time_difference(self.last_generation_time, generation_time)

        self.last_generation_time = generation_time
        return result

    found_anomalies = 0
    seed_history = []

    def write_anomalies(self):
        file_path = os.path.join(output_dir, f"out_{self.found_anomalies}")
        os.makedirs(file_path, exist_ok=True)

        for i, byte_data in enumerate(self.seed_history):
            file_name = f"{file_path}/seed_{i}.bin"
            with open(file_name, "wb") as file:
                file.write(byte_data)
        self.found_anomalies = self.found_anomalies + 1

    def fuzz_loop(self, rec, send):
        for i in range(20):
            try:
                data = rec()
                self.handle_packet(data)
            except TargetNotResponding:
                logging.error("The target device is not responding. Make sure it's accessible.")
                return

        while True:
            for index, seed in enumerate(get_seeds(input_dir)):
                self.seed_history.append(seed)
                # UDP send
                # to_send = Ether(dst="ff:ff:ff:ff:ff:ff", src="ff:00:00:00:00:01", type=0x8947) / Raw(load=seed)
                #to_send = (Dot11(subtype=8, type=2, proto=0, ID=0, addr1='ff:ff:ff:ff:ff:ff', addr2='98:75:2f:8a:77:13',
                #                 addr3='ff:ff:ff:ff:ff:ff', SC=4080) /
                #           Dot11QoS(A_MSDU_Present=0, Ack_Policy=1, EOSP=0, TID=3, TXOP=0) /
                #           LLC(dsap=170, ssap=170, ctrl=3) /
                #           SNAP(OUI=0, code=35143) /
                #           Raw(load=seed))
                to_send = Ether(dst='ff:ff:ff:ff:ff:ff', src='00:e0:4c:68:8d:cd', type=35143) / Raw(load=bytes(seed))
                send(raw(to_send))

                if index % num_samples_before_check == 0:
                    try:
                        data = rec()
                        result = self.handle_packet(data)
                    except TargetNotResponding:
                        logging.info(f"The target device is not responding anymore 😔")
                        result = PacketHandlingResult.NOT_RESPONDING

                    match result:
                        case PacketHandlingResult.ABNORMAL:
                            self.write_anomalies()
                        case PacketHandlingResult.NOT_RESPONDING:
                            self.write_anomalies()
                            should_continue = input('Continue? (y/n).\n')
                            if should_continue != "y":
                                return

                    self.seed_history.clear()

    def handle_packet(self, dissected: Packet) -> PacketHandlingResult:
        print(dissected.command())

        if GeoBasicHeader not in dissected:
            logging.info(f"Received message is not C-ITS, skipping")
            return PacketHandlingResult.SKIPPED

        if ITS_CAM not in dissected:
            logging.info("Received message is not CAM, skipping")
            return PacketHandlingResult.SKIPPED

        latitude = coord_to_double(dissected[SingleHopBroadcast].latitude)
        longitude = coord_to_double(dissected[SingleHopBroadcast].longitude)

        # position = (latitude, longitude)

        # distance = geodesic(self.position_watched, position).meters

        # if distance > 50 and self.position_watched is not None:
        #    logging.info(f"Received message from {distance}m away foreign device, skipping")
        #    return PacketHandlingResult.SKIPPED

        # if self.position_watched is None:
        #    self.position_watched = position

        generation_delta_time = dissected[ITS_CAM].asn1.get_val_at(['cam', 'generationDeltaTime'])
        print(generation_delta_time)
        generation_delta_time_delta = self.calc_generation_time_delta(generation_delta_time)
        if generation_delta_time_delta is not None:
            self.generation_time_history.append(generation_delta_time_delta)

        if generation_delta_time_delta is None:
            return PacketHandlingResult.PROBABLY_OKAY

        if generation_delta_time_delta > 210:
            logging.info(f"{generation_delta_time_delta} - unusual high generation time interval deviation!")
            return PacketHandlingResult.ABNORMAL
        elif generation_delta_time_delta < 190:
            logging.info(f"{generation_delta_time_delta} - unusual low generation time interval deviation!")
            return PacketHandlingResult.ABNORMAL
        else:
            logging.info(generation_delta_time_delta)
            return PacketHandlingResult.OKAY


class SSHFuzz(PacketHandler):
    def __init__(self):
        self.client = None
        self.stdout = None

    def receive_ssh(self):
        while True:
            line = self.stdout.readline()
            print(line)
            if not line:
                continue

            message = line.strip()
            logging.info(f"Received: {message}")
            try:
                stdout_bytes = bytes.fromhex(message)
            except ValueError:
                logging.error("Received invalid hex string")
                continue

            return Dot11(stdout_bytes)

    def send_ssh(self, to_send: bytes):
        self.client.exec_command(f"sudo llc tx {to_send.hex()}")
        print("send!!!!!!!!!!!!!!!!!")

    def handle_stdout(self, stdout_line):
        message = stdout_line.strip()
        logging.info(f"Received: {message}")
        try:
            stdout_bytes = bytes.fromhex(message)
        except ValueError:
            logging.error("Received invalid hex string")
            return

        dissected = Dot11(stdout_bytes)
        print(dissected.show(dump=True))
        self.handle_packet(dissected)

    def ssh_loop(self):
        logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
        host = "172.31.31.60"
        username = "user"
        password = "user"
        # Create an SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            # Connect to the device
            client.connect(host, username=username, password=password)
            self.client = client

            _, stdout, _ = client.exec_command("sudo llc rx")
            self.stdout = stdout

            self.fuzz_loop(self.receive_ssh, self.send_ssh)

        except paramiko.AuthenticationException:
            logging.error("Authentication failed. Please check your credentials.")
        except paramiko.SSHException as e:
            logging.error(f"SSH error: {e}")
        finally:
            client.close()


class UDPFuzz(PacketHandler):
    def create_socket(self, multicast_ip, port):
        """
        Creates a socket, sets the necessary options on it, then binds it. The socket is then returned for use.
        """

        local_ip = "172.31.31.61"

        # create a UDP socket
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # allow reuse of addresses
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # set multicast interface to local_ip
        my_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(local_ip))

        # Set multicast time-to-live to 2...should keep our multicast packets from escaping the local network
        my_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        # Construct a membership request...tells router what multicast group we want to subscribe to
        membership_request = socket.inet_aton(multicast_ip) + socket.inet_aton(local_ip)
        my_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership_request)

        # Bind the socket to an interface.
        my_socket.bind((local_ip, port))

        my_socket.setblocking(False)

        return my_socket

    def prepare_loop(self):
        multicast_ip = udp_device_ip
        port = udp_device_port
        udp_socket = self.create_socket(multicast_ip, port)

        def receive_udp():
            while True:
                ready = select.select([udp_socket], [], [], 3)
                if ready[0]:
                    data, address = udp_socket.recvfrom(4096)
                    if address[0] == '172.31.31.60':
                        break
                else:
                    raise TargetNotResponding
            return Ether(data)

        def send_udp(to_send: bytes):
            udp_socket.sendto(to_send, (udp_device_ip, udp_device_port))

        self.fuzz_loop(receive_udp, send_udp)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    parser = argparse.ArgumentParser(description="Blackbox fuzzer for ITS protocol")
    parser.add_argument("--input", type=str, required=True, help="Path to input directory")
    parser.add_argument("--output", type=str, required=True, help="Path to output directory")
    parser.add_argument("--num_samples", type=int, default=12, help="Number of samples before checking")
    args = parser.parse_args()

    # Uncomment the following line to use SSHFuzz
    fuzzer = SSHFuzz()
    fuzzer.ssh_loop()

    # Use UDPFuzz
    # fuzzer = UDPFuzz()
    # fuzzer.prepare_loop()
