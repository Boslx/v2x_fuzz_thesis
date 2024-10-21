import xml.etree.cElementTree as ET

from deepdiff import DeepDiff
from matplotlib import pyplot as plt
from pycrate_asn1dir import ITS_CAM_2, ITS_DENM_3
from pycrate_asn1rt.asnobj import ASN1Obj
from pathlib import Path

from scapy_etsi_its.Etsi_Its_Msgs import *


import copy


def get_seed_bytes(secure_bytes: bytes) -> bytes:
    seed_package = (Ether(dst="ff:ff:ff:ff:ff:ff", src="ff:00:00:00:00:01", type=0x8947)
                    / GeoBasicHeader(NH=2)
                    / Raw(load=secure_bytes))

    # Calculate checksums etc.
    seed_package.show2(dump=True)
    return raw(seed_package)


def fuzz(input_asn1, num_expand=1, max_count_seeds=300):
    ident_history_guided = {}

    input_asn1_proto_guided = input_asn1.get_proto(ident_history=ident_history_guided)
    for _ in itertools.repeat(None, num_expand):
        input_asn1_proto_guided.expand_once(ident_history_guided)

    input_asn1_proto_guided.remove_expandable()

    save_fuzz(input_asn1, input_asn1_proto_guided, max_count_seeds)


def save_fuzz(input_asn1, input_asn1_proto_guided, max_count_seeds):
    output_dir = f"D:\\Projects\\v2x-fuzz-thesis\\experiments\\seed_generation\\facilities\\new\\{input_asn1.fullname()}"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for count in range(max_count_seeds):
        fuzzed = input_asn1_proto_guided.fuzz(None, None, True, 1)
        input_asn1.set_val(fuzzed)

        with open(f"{output_dir}\\{count}.bin", "wb") as binary_file:
            binary_file.write(get_seed_bytes(bytes(input_asn1.to_coer())))

        if input_asn1_proto_guided.fully_covered:
            break


def main():
    features = [Ieee1609Dot2.Ieee1609Dot2Data]
    for feature in features:
        fuzz(feature)


if __name__ == "__main__":
    main()
