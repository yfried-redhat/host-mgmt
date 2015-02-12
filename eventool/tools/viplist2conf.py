import argparse
import sys
import yaml


def gen_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fromfile")
    parser.add_argument("--tofile")
    parser.add_argument("--vip-suffix", default="_vip:")

    return parser.parse_args()


def core():
    args = gen_parser()
    with open(args.fromfile, "r") as input:
        output_yml = {}
        while True:
            l1 = input.readline()
            l2 = input.readline()
            if not l2:
                break
            if l1.strip().endswith(args.vip_suffix):
                alias = l1.strip(":\n")
                address = l2.strip()
                output_yml[address] = {"alias": [alias]}

    with open(args.tofile, "wb") as output:
        output.write(yaml.safe_dump({"vip": output_yml}, default_flow_style=False))


if __name__ == '__main__':
    sys.exit(core())
