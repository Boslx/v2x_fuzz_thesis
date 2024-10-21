from scapy_etsi_its.Etsi_Its_Msgs import *

container_ip = "239.118.122.97"
container_port = 8947


def main():
    parser = argparse.ArgumentParser(description="Generate messages out of the products")
    parser.add_argument("file_path", help="Path to the file you want to send")
    args = parser.parse_args()

    if os.path.isfile(args.file_path):
        send_file(args.file_path)
    else:
        print(f"File not found: {args.file_path}")


def send_file(file_path):
    with open(file_path, "rb") as file:
        file_bytes = file.read()
        toDissect = GeoBasicHeader(bytes(file_bytes))
        print(toDissect.show(dump=True))

        nasty = Ether(dst="ff:ff:ff:ff:ff:ff", src="ff:00:00:00:00:01", type=0x8947) / Raw(load=file_bytes)
        nasty.show2(dump=True)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Specify special interfaces here
        # sock.setsockopt(socket.SOL_SOCKET, 25, str("enx001217f23daa" + '\0').encode('utf-8'))
        sock.bind(('192.168.88.1', 0))
        sock.sendto(raw(nasty), (container_ip, container_port))
        print(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))


if __name__ == "__main__":
    main()
