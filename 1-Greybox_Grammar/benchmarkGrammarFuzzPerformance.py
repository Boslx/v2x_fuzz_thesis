import timeit
from scapy_etsi_its.Etsi_Its_Msgs import *


def cov_samples(num_expand=0, max_count_seeds=5000):
    input_asn1 = Ieee1609Dot2.Ieee1609Dot2Data
    ident_history_guided = {}

    input_asn1_proto_guided = input_asn1.get_proto(ident_history=ident_history_guided)
    for _ in itertools.repeat(None, num_expand):
        input_asn1_proto_guided.expand_once(ident_history_guided)

    input_asn1_proto_guided.remove_expandable()

    save_fuzz(input_asn1_proto_guided, max_count_seeds)


def save_fuzz(input_asn1_proto_guided, max_count_seeds):
    def fuzz_and_send():
        fuzzed = input_asn1_proto_guided.fuzz(None, None, False, 1)
        to_send = Ieee1609Dot2.Ieee1609Dot2Data
        to_send.set_val(fuzzed)

        test = GeoBasicHeader()

        seed_package = (Ether(dst="ff:ff:ff:ff:ff:ff", src="ff:00:00:00:00:01", type=0x8947)
                        / GeoBasicHeader(NH=2)
                        / Raw(load=bytes(to_send.to_oer())))

        # Calculate checksums etc.
        seed_package.show2(dump=True)

    # Measure execution time
    elapsed_time = timeit.timeit(fuzz_and_send, number=max_count_seeds)
    print(f"Total execution time for {max_count_seeds} iterations: {elapsed_time:.4f} seconds")


def main():
    cov_samples()


if __name__ == "__main__":
    main()
