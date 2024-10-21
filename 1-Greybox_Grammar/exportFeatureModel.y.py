import xml.etree.cElementTree as ET

from pycrate_asn1rt.asnobj import ASN1Obj

from scapy_etsi_its.Etsi_Its_Msgs import *

graphics_attributes = [
    {"key": "autolayoutconstraints", "value": "false"},
    {"key": "legendautolayout", "value": "true"},
    {"key": "showconstraints", "value": "true"},
    {"key": "showshortnames", "value": "false"},
    {"key": "layout", "value": "horizontal"},
    {"key": "showcollapsedconstraints", "value": "true"},
    {"key": "legendhidden", "value": "false"},
    {"key": "layoutalgorithm", "value": "1"}
]


def export_feature_model(input_asn1: ASN1Obj, num_expand=0):
    ident_history = {}
    input_proto = input_asn1.get_proto(ident_history=ident_history)

    for _ in itertools.repeat(None, num_expand):
        input_proto.expand_once(ident_history)

    input_proto.remove_expandable()
    root = ET.Element("featureModel")
    properties = ET.SubElement(root, "properties")
    for attr in graphics_attributes:
        graphics = ET.SubElement(properties, "graphics", attrib=attr)

    struct_root = ET.SubElement(root, "struct")
    input_proto.feature_ide(struct_root, {})

    tree = ET.ElementTree(root)
    tree.write(f"FeatureModels/{input_asn1.fullname()}.xml")


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
        export_feature_model(feature)

# Creates a Feature Model for FeatureIDE https://featureide.github.io/
if __name__ == "__main__":
    main()
