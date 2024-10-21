import itertools

from matplotlib import pyplot as plt
from pycrate_asn1dir import ITS_CAM_2, ITS_DENM_3
from pycrate_asn1dir.ITS import IVIM_PDU_Descriptions, SREM_PDU_Descriptions
from pycrate_asn1dir.ITS_IEEE1609_2 import Ieee1609Dot2
from pycrate_asn1dir.ITS_IS import MAPEM_PDU_Descriptions
from pycrate_asn1dir.ITS_r1318 import SPATEM_PDU_Descriptions, SSEM_PDU_Descriptions, EVCSN_PDU_Descriptions
from pycrate_asn1rt.asnobj import ASN1Obj


def calculate_coverage(input_asn1: ASN1Obj, num_expand=0):
    ident_history_guided = {}
    ident_history_unguided = {}

    input_asn1_proto_guided = input_asn1.get_proto(ident_history=ident_history_guided)
    input_asn1_proto_unguided = input_asn1.get_proto(ident_history=ident_history_unguided)
    for _ in itertools.repeat(None, num_expand):
        input_asn1_proto_guided.expand_once(ident_history_guided)
        input_asn1_proto_unguided.expand_once(ident_history_unguided)

    input_asn1_proto_guided.remove_expandable()
    input_asn1_proto_unguided.remove_expandable()

    max_coverage = []
    current_coverage_guided = [0]
    current_coverage_unguided = [0]

    # last_one = None

    max_cov = 0

    for count in range(300):
        guided = input_asn1_proto_guided.fuzz(None, None, True, 1)
        unguided = input_asn1_proto_unguided.fuzz(None, None, False, 1)

        coverage_guided = input_asn1_proto_guided.coverage()
        coverage_unguided = input_asn1_proto_unguided.coverage()

        max_coverage.append(coverage_guided[0])
        current_coverage_guided.append(coverage_guided[1])
        current_coverage_unguided.append(coverage_unguided[1])

        if input_asn1_proto_guided.fully_covered and max_cov == 0:
            max_cov = count

        if input_asn1_proto_unguided.fully_covered:
            break

    print(f"{input_asn1.fullname()} rand count = {len(current_coverage_guided)}, max cov count = {max_cov}")
    f = plt.figure(figsize=(5, 2))
    # plt.plot(max_coverage, label="max cov")
    plt.axhline(y=max_coverage[0], color='r', linestyle='--')
    plt.plot(current_coverage_guided, label="cov guided")
    plt.plot(current_coverage_unguided, label="cov unguided")
    plt.xlabel("Fuzz Iteration")
    plt.ylabel("Coverage")
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    features = [Ieee1609Dot2.Ieee1609Dot2Data,
                ITS_CAM_2.CAM_PDU_Descriptions.CAM,
                ITS_DENM_3.DENM_PDU_Descriptions.DENM,
                MAPEM_PDU_Descriptions.MAPEM,
                SPATEM_PDU_Descriptions.SPATEM,
                IVIM_PDU_Descriptions.IVIM,
                SREM_PDU_Descriptions.SREM,
                SSEM_PDU_Descriptions.SSEM,
                EVCSN_PDU_Descriptions.EvcsnPdu
                ]

    for feature in features:
        calculate_coverage(feature)


if __name__ == "__main__":
    main()
