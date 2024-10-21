import xml.etree.cElementTree as ET

from deepdiff import DeepDiff
from matplotlib import pyplot as plt
from pycrate_asn1dir import ITS_CAM_2, ITS_DENM_3
from pycrate_asn1rt.asnobj import ASN1Obj

from scapy_etsi_its.Etsi_Its_Msgs import *



def get_seed_bytes(secure_bytes: bytes) -> bytes:
    # seed_package = (Ether(dst="ff:ff:ff:ff:ff:ff", src="ff:00:00:00:00:01", type=0x8947)
    #                / GeoBasicHeader(NH=2)
    #                / Raw(load=secure_bytes))

    # Calculate checksums etc.
    # seed_package.show2(dump=True)
    # return raw(seed_package)
    return secure_bytes


def t_wise_sample(folder_path, num_expand=0):
    input_asn1 = Ieee1609Dot2.Ieee1609Dot2Data
    ident_history_guided = {}

    input_asn1_proto_guided = input_asn1.get_proto(ident_history=ident_history_guided)
    for _ in itertools.repeat(None, num_expand):
        input_asn1_proto_guided.expand_once(ident_history_guided)

    input_asn1_proto_guided.remove_expandable()

    for filename in os.listdir(folder_path):
        if filename.endswith('.config'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                allow_list = set(file.read().replace("seq_", "").splitlines())
                fuzzed = input_asn1_proto_guided.fuzz(allow_list, None, False, 1)
                to_send = Ieee1609Dot2.Ieee1609Dot2Data
                to_send.set_val(fuzzed)

                with open(f"D:\\Projects\\v2x-fuzz-thesis\\experiments\\seed_generation\\basicSecureLayer\\t-wise\\{filename}.bin",
                          "wb") as binary_file:
                    binary_file.write(get_seed_bytes(bytes(to_send.to_oer())))


def main():
    t_wise_sample("C:\\Users\\lbosch\\Downloads\\featureide\\workspace\\IEEE1609\\productst2")


if __name__ == "__main__":
    main()
