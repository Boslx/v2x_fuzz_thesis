import hashlib

from ecdsa import VerifyingKey, NIST256p
from ecdsa.util import sigdecode_strings
from pycrate_asn1dir import ITS_CAM_2
from pycrate_asn1dir.ITS_IEEE1609_2 import Ieee1609Dot2

from scapy_etsi_its.Etsi_Its_Msgs import *


class CompressionState(Enum):
    COMPRESSED_Y_0 = 0x02
    COMPRESSED_Y_1 = 0x03
    UNCOMPRESSED = 0x04


def show_packets(pcap_file):
    """
    Displays each packet in the given pcapng file.
    """
    packets = rdpcap(pcap_file)
    for packet in packets:
        dissect_cam(packet)


def ecdsa_nist_p256(r: bytearray, s: bytearray, curve_point: bytearray, msg, encoded_certificate):
    curve_point.insert(0, 0x02)
    vk = VerifyingKey.from_string(curve_point, curve=NIST256p, hashfunc=hashlib.sha256)
    concat = hashlib.sha256(msg).digest() + hashlib.sha256(encoded_certificate).digest()

    return vk.verify((r, s), concat, hashlib.sha256, sigdecode=sigdecode_strings)


def dissect_cam(packet):
    if GeoBasicHeader in packet:
        print(packet.show2(dump=True))

        raw_secure_header = packet[Raw].load
        print(raw_secure_header.hex())
        secure_header = Ieee1609Dot2.Ieee1609Dot2Data
        secure_header.from_coer(raw_secure_header)
        data = secure_header.get_at(["content", "signedData", "tbsData"])
        data_raw = data.to_coer()
        secure_header_values = secure_header.get_val()
        verifying_key = secure_header_values['content'][1]['signer'][1][0]['toBeSigned']['verifyKeyIndicator'][1][1][1]
        # compressed y0 (0x02)
        # compressed y1 (0x03)
        # uncompressed (0x04)
        # verifying_key.insert(0, 0x02)

        certificate = secure_header.get_at(["content", "signedData", "signer", "certificate"])
        certificate_raw = certificate.to_coer()

        signature = secure_header_values['content'][1]['signature'][0]

        r_sig = secure_header_values['content'][1]['signer'][1][0]['signature'][1]['rSig'][1]
        s_sig = secure_header_values['content'][1]['signer'][1][0]['signature'][1]['sSig']

        match signature:
            case "ecdsaNistP256Signature":
                result = ecdsa_nist_p256(bytearray(r_sig), bytearray(s_sig), bytearray(verifying_key), data_raw,
                                         certificate_raw)
                print(result)

        print(data.to_json())
        print(data_raw.hex())

        print(secure_header.to_json())

        # secure_header_values = secure_header.get_val()

        payload = secure_header_values['content'][1]['tbsData']['payload']['data']['content'][1]
        common_header = GeoCommonHeader(payload)
        print(common_header.show2(dump=True))

        if BTPB in common_header and common_header[BTPB].dport == 2001:
            raw_cam = common_header[Raw].load
            cam = ITS_CAM_2.CAM_PDU_Descriptions.CAM
            krankesProto = cam.get_proto()
            cam.from_uper(raw_cam)
            print(cam.to_json())
            print("Läuft")


certificateMessage = [0x12, 0x00, 0x05, 0x01, 0x03, 0x81, 0x00, 0x40, 0x03, 0x80, 0x56, 0x20, 0x50, 0x02, 0x80, 0x00,
                      0x32, 0x01, 0x00, 0x14, 0x00, 0xfe, 0x38, 0x4c, 0xe0, 0xb8, 0x90, 0xbf, 0x6b, 0x33, 0x44, 0x1f,
                      0x45, 0x28, 0x40, 0x06, 0x64, 0x0c, 0x70, 0x81, 0xae, 0x03, 0xbd, 0x00, 0x00, 0xa0, 0x00, 0x07,
                      0xd1, 0x00, 0x00, 0x02, 0x02, 0x4c, 0xe0, 0xb8, 0x90, 0x35, 0x71, 0x00, 0x5a, 0x9d, 0x42, 0x25,
                      0xee, 0x35, 0xbb, 0xfc, 0x82, 0x4a, 0x24, 0x46, 0xd8, 0x35, 0xa3, 0x54, 0x58, 0x3b, 0xe1, 0x21,
                      0x00, 0x83, 0x02, 0x96, 0x8a, 0xaf, 0x33, 0xf0, 0x81, 0xfe, 0x9a, 0x10, 0x3f, 0xa0, 0x14, 0x19,
                      0x80, 0x40, 0x01, 0x24, 0x00, 0x01, 0xc8, 0x0b, 0xba, 0xc9, 0x16, 0xae, 0x81, 0x01, 0x01, 0x80,
                      0x03, 0x00, 0x80, 0x56, 0xdf, 0xd6, 0xd6, 0x27, 0xa3, 0x62, 0xdc, 0x10, 0x83, 0x00, 0x00, 0x00,
                      0x00, 0x00, 0x1d, 0xdf, 0xf7, 0xb5, 0x84, 0x00, 0xa8, 0x01, 0x02, 0x80, 0x01, 0x24, 0x81, 0x04,
                      0x03, 0x01, 0x00, 0x00, 0x80, 0x01, 0x25, 0x81, 0x05, 0x04, 0x01, 0x90, 0x1a, 0x25, 0x80, 0x80,
                      0x82, 0x04, 0x27, 0xbb, 0x27, 0xc9, 0x98, 0xc1, 0xec, 0xa2, 0xb1, 0x0e, 0x71, 0x07, 0x98, 0x02,
                      0x44, 0x51, 0x8b, 0x3c, 0x50, 0xa3, 0xa3, 0x27, 0xb5, 0xb1, 0x90, 0xd0, 0x90, 0xf1, 0x45, 0x1f,
                      0x3d, 0x80, 0x80, 0x83, 0xc2, 0xf3, 0xca, 0xeb, 0xc7, 0xfa, 0x35, 0x94, 0x5c, 0x03, 0x0a, 0x5a,
                      0xe0, 0x1a, 0x41, 0x7a, 0xdf, 0x6d, 0xff, 0xd5, 0x41, 0xcc, 0xd2, 0xd9, 0x2b, 0xfe, 0xb6, 0x3d,
                      0xc1, 0x56, 0x89, 0xcb, 0xd6, 0xb8, 0xe3, 0x2b, 0xd5, 0xe8, 0x66, 0xd9, 0xfa, 0xa2, 0xfe, 0x55,
                      0x95, 0xe2, 0xdb, 0xb9, 0xbe, 0x3e, 0x96, 0x5a, 0x70, 0x94, 0x25, 0x8b, 0x4a, 0x24, 0x9d, 0xfb,
                      0x75, 0x8a, 0x07, 0x80, 0x82, 0xf4, 0x4c, 0xc3, 0xc3, 0xb1, 0x0c, 0xf7, 0x7c, 0xd9, 0x0c, 0x40,
                      0xfe, 0xe7, 0x30, 0x40, 0xad, 0x0b, 0xb4, 0xf8, 0x34, 0x55, 0x81, 0x37, 0xa6, 0x96, 0x81, 0x78,
                      0xe0, 0x53, 0x09, 0x06, 0xf7, 0x4f, 0x14, 0x43, 0x46, 0x88, 0x29, 0x6e, 0x22, 0xfe, 0xbb, 0x6f,
                      0x8e, 0x21, 0xad, 0x51, 0x7e, 0xb0, 0x81, 0x9a, 0x39, 0xf2, 0xaa, 0xd3, 0x37, 0x51, 0xf3, 0xab,
                      0xde, 0xdd, 0x69, 0xfe, 0xaf]

# Example usage:
if __name__ == "__main__":
    # pcap_file_path = r"C:\Users\lbosch\Desktop\tmp\TraceV2X.pcapng"
    # show_packets(pcap_file_path)
    print(ecdsa_nist_p256(bytearray(
        [0x83, 0xC2, 0xF3, 0xCA, 0xEB, 0xC7, 0xFA, 0x35, 0x94, 0x5C, 0x03, 0x0A, 0x5A, 0xE0, 0x1A, 0x41, 0x7A, 0xDF,
         0x6D, 0xFF, 0xD5, 0x41, 0xCC, 0xD2, 0xD9, 0x2B, 0xFE, 0xB6, 0x3D, 0xC1, 0x56, 0x89]),
        bytearray(
            [0xCB, 0xD6, 0xB8, 0xE3, 0x2B, 0xD5, 0xE8, 0x66, 0xD9, 0xFA, 0xA2, 0xFE, 0x55, 0x95, 0xE2, 0xDB, 0xB9, 0xBE,
             0x3E, 0x96, 0x5A, 0x70, 0x94, 0x25, 0x8B, 0x4A, 0x24, 0x9D, 0xFB, 0x75, 0x8A, 0x07]),
        bytearray(
            [0x04, 0x27, 0xBB, 0x27, 0xC9, 0x98, 0xC1, 0xEC, 0xA2, 0xB1, 0x0E, 0x71, 0x07, 0x98, 0x02, 0x44, 0x51, 0x8B,
             0x3C, 0x50, 0xA3, 0xA3, 0x27, 0xB5, 0xB1, 0x90, 0xD0, 0x90, 0xF1, 0x45, 0x1F, 0x3D]),
        bytearray(
            [0x40, 0x03, 0x80, 0x56, 0x20, 0x50, 0x02, 0x80, 0x00, 0x32, 0x01, 0x00, 0x14, 0x00, 0xFE, 0x38, 0x4C, 0xE0,
             0xB8, 0x90, 0xBF, 0x6B, 0x33, 0x44, 0x1F, 0x45, 0x28, 0x40, 0x06, 0x64, 0x0C, 0x70, 0x81, 0xAE, 0x03, 0xBD,
             0x00, 0x00, 0xA0, 0x00, 0x07, 0xD1, 0x00, 0x00, 0x02, 0x02, 0x4C, 0xE0, 0xB8, 0x90, 0x35, 0x71, 0x00, 0x5A,
             0x9D, 0x42, 0x25, 0xEE, 0x35, 0xBB, 0xFC, 0x82, 0x4A, 0x24, 0x46, 0xD8, 0x35, 0xA3, 0x54, 0x58, 0x3B, 0xE1,
             0x21, 0x00, 0x83, 0x02, 0x96, 0x8A, 0xAF, 0x33, 0xF0, 0x81, 0xFE, 0x9A, 0x10, 0x3F, 0xA0, 0x14, 0x19, 0x80,
             0x40, 0x01, 0x24, 0x00, 0x01, 0xC8, 0x0B, 0xBA, 0xC9, 0x16, 0xAE, ]),
        bytearray(
            [0x80, 0x03, 0x00, 0x80, 0x56, 0xDF, 0xD6, 0xD6, 0x27, 0xA3, 0x62, 0xDC, 0x10, 0x83, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x1D, 0xDF, 0xF7, 0xB5, 0x84, 0x00, 0xA8, 0x01, 0x02, 0x80, 0x01, 0x24, 0x81,
             0x04, 0x03, 0x01, 0x00, 0x00, 0x80, 0x01, 0x25, 0x81, 0x05, 0x04, 0x01, 0x90, 0x1A, 0x25, 0x80,
             0x80, 0x82, 0x04, 0x27, 0xBB, 0x27, 0xC9, 0x98, 0xC1, 0xEC, 0xA2, 0xB1, 0x0E, 0x71, 0x07, 0x98,
             0x02, 0x44, 0x51, 0x8B, 0x3C, 0x50, 0xA3, 0xA3, 0x27, 0xB5, 0xB1, 0x90, 0xD0, 0x90, 0xF1, 0x45,
             0x1F, 0x3D, 0x80, 0x80, 0x83, 0xC2, 0xF3, 0xCA, 0xEB, 0xC7, 0xFA, 0x35, 0x94, 0x5C, 0x03, 0x0A,
             0x5A, 0xE0, 0x1A, 0x41, 0x7A, 0xDF, 0x6D, 0xFF, 0xD5, 0x41, 0xCC, 0xD2, 0xD9, 0x2B, 0xFE, 0xB6,
             0x3D, 0xC1, 0x56, 0x89, 0xCB, 0xD6, 0xB8, 0xE3, 0x2B, 0xD5, 0xE8, 0x66, 0xD9, 0xFA, 0xA2, 0xFE,
             0x55, 0x95, 0xE2, 0xDB, 0xB9, 0xBE, 0x3E, 0x96, 0x5A, 0x70, 0x94, 0x25, 0x8B, 0x4A, 0x24, 0x9D,
             0xFB, 0x75, 0x8A, 0x07, ])))

    dissect_cam(GeoBasicHeader(bytes(certificateMessage)))
    print(ecdsa_nist_p256(bytearray(
        [0x3c, 0xa4, 0x68, 0x09, 0x0a, 0xeb, 0xdd, 0x3e, 0x63, 0xaf, 0x42, 0x1a, 0x91, 0x10, 0x17, 0x76, 0x98, 0x9b,
         0x32, 0xef, 0x64, 0xbf, 0x00, 0x5d, 0x4c, 0x10, 0x44, 0xd6, 0x88, 0x79, 0x49, 0x9b]), bytearray(
        [0xb6, 0xd4, 0xbe, 0x84, 0xb3, 0x31, 0x86, 0x96, 0x80, 0x46, 0xff, 0xa3, 0x48, 0xc1, 0xe8, 0x6a, 0x0a, 0x9c,
         0xa0, 0x71, 0x2c, 0xa6, 0xd0, 0x4f, 0x93, 0x4e, 0x92, 0xcc, 0x99, 0x45, 0xd2, 0xe8]), bytearray(
        [0x13, 0x43, 0x08, 0xc4, 0x32, 0x4d, 0x5f, 0x47, 0xfc, 0xbe, 0x66, 0x5f, 0xb5, 0x5b, 0x40, 0x98, 0xb3, 0x8b,
         0x9c, 0xaa, 0x48, 0x4b, 0xd4, 0x47, 0x4c, 0x6c, 0x52, 0x16, 0x00, 0xa7, 0x50, 0x8c]), bytearray(
        [0x40, 0x03, 0x80, 0x78, 0x20, 0x50, 0x02, 0x80, 0x00, 0x54, 0x01, 0x00, 0x14, 0x00, 0xca, 0x83, 0x1a, 0x3f,
         0x3d, 0x39, 0x70, 0xfc, 0x86, 0x68, 0x1f, 0xeb, 0x32, 0x07, 0x05, 0xec, 0x3a, 0xd3, 0x80, 0x04, 0x0b, 0x90,
         0x00, 0x00, 0x00, 0x00, 0x07, 0xd1, 0x00, 0x00, 0x02, 0x02, 0x1a, 0x3f, 0x3d, 0x39, 0x86, 0x68, 0x40, 0x5a,
         0xb2, 0x03, 0x60, 0xee, 0x26, 0xc1, 0x9a, 0x60, 0xb0, 0x0b, 0x00, 0x00, 0x34, 0x87, 0x8e, 0x48, 0xb9, 0x1f,
         0xa0, 0x01, 0x10, 0x82, 0xe8, 0x92, 0x83, 0x33, 0xff, 0x01, 0xff, 0xfa, 0x00, 0x28, 0x33, 0x00, 0x00, 0x4b,
         0xff, 0x74, 0xff, 0x2a, 0x2e, 0x68, 0x0c, 0xbb, 0xdf, 0xa4, 0x48, 0x24, 0x7e, 0x23, 0xd3, 0xc8, 0x1f, 0x02,
         0x4a, 0xbe, 0xa5, 0xe8, 0xcf, 0x09, 0x69, 0xf8, 0x0d, 0xed, 0xf4, 0x24, 0x4c, 0x90, 0x33, 0x3f, 0x40, 0x01,
         0x24, 0x00, 0x02, 0x30, 0x51, 0x5a, 0x70, 0x30, 0x2c]), bytearray(
        [0x80, 0x03, 0x00, 0x80, 0x5d, 0x5d, 0xcb, 0xee, 0xfb, 0xe7, 0xd2, 0x2d, 0x30, 0x83, 0x00, 0x00, 0x00, 0x00,
         0x00, 0x24, 0x81, 0xd9, 0x85, 0x86, 0x00, 0x01, 0xe0, 0x01, 0x07, 0x80, 0x01, 0x24, 0x81, 0x04, 0x03, 0x01,
         0xff, 0xfc, 0x80, 0x01, 0x25, 0x81, 0x05, 0x04, 0x01, 0xff, 0xff, 0xff, 0x80, 0x01, 0x8c, 0x81, 0x05, 0x04,
         0x02, 0xff, 0xff, 0xe0, 0x00, 0x01, 0x8d, 0x80, 0x02, 0x02, 0x7e, 0x81, 0x02, 0x01, 0x01, 0x80, 0x02, 0x02,
         0x7f, 0x81, 0x02, 0x01, 0x01, 0x00, 0x02, 0x03, 0xff, 0x80, 0x80, 0x82, 0x13, 0x43, 0x08, 0xc4, 0x32, 0x4d,
         0x5f, 0x47, 0xfc, 0xbe, 0x66, 0x5f, 0xb5, 0x5b, 0x40, 0x98, 0xb3, 0x8b, 0x9c, 0xaa, 0x48, 0x4b, 0xd4, 0x47,
         0x4c, 0x6c, 0x52, 0x16, 0x00, 0xa7, 0x50, 0x8c, 0x81, 0x80, 0x3d, 0x9a, 0x96, 0x8a, 0xc1, 0x19, 0x6e, 0x46,
         0xea, 0x98, 0x22, 0x6c, 0x55, 0x20, 0x81, 0xa7, 0x7c, 0xdf, 0xbe, 0xd5, 0x8c, 0x76, 0x9a, 0xf2, 0x8c, 0x9f,
         0xf9, 0x06, 0xe9, 0x26, 0xd9, 0x22, 0x40, 0x5f, 0x18, 0x9a, 0x1c, 0x6a, 0x03, 0x19, 0x89, 0x68, 0x96, 0x0a,
         0x93, 0x32, 0x50, 0x06, 0xaf, 0xfb, 0x84, 0x40, 0x4c, 0x93, 0x16, 0x80, 0x69, 0x8f, 0xff, 0x27, 0xc8, 0xf3,
         0x12, 0x7e, ])))
