"""CLI:  python -m kappagate run [--mode mock|cache|live] [--record]
        python -m kappagate gate"""
import argparse
import json
import sys

from . import harness, gate


def main():
    ap = argparse.ArgumentParser(prog="kappagate")
    sub = ap.add_subparsers(dest="cmd", required=True)
    runp = sub.add_parser("run", help="judge the golden set and write results/")
    runp.add_argument("--mode", choices=("mock", "cache", "live"), default="mock")
    runp.add_argument("--record", action="store_true",
                      help="live mode: record judgments to cache/ for replay")
    sub.add_parser("gate", help="apply the calibration gate to results/report.json")
    args = ap.parse_args()
    if args.cmd == "run":
        summary = harness.run(mode=args.mode, record=args.record)
        print(json.dumps(summary, indent=2))
    else:
        sys.exit(gate.check())


if __name__ == "__main__":
    main()
