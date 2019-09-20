"""
Read a PMSx003 sensor and print PM measurements

Usage:
     pms serial [options]

Options:
    -s, --serial <port>     serial port [default: /dev/ttyUSB0]
    -n, --interval <secs>   seconds to wait between updates [default: 60]
    -f, --format <fmt>      (pm|num|csv)formatted output  [default: pm]
    --help                  display this help and exit

NOTE:
Environment variables take precedence over command line options
- PMS_INTERVAL      overrides -n, --interval
- PMS_SERIAL        overrides -s, --serial
- PMS_FORMAT        overrides -f, --format
"""

import os
from typing import Dict, List, Union, Any, Optional
from docopt import docopt
from pms import PMSerial


def parse_args(args: Dict[str, str]) -> Dict[str, Any]:
    return dict(
        interval=int(os.environ.get("PMS_INTERVAL", args["--interval"])),
        serial=os.environ.get("PMS_SERIAL", args["--serial"]),
        format=os.environ.get("PMS_FORMAT", args["--format"]),
    )


def main(interval: int, serial: str, format: bool) -> None:
    with PMSerial(serial) as read:
        for pm in read(interval):
            print(f"{pm:{format}}")


def cli(argv: Optional[List[str]] = None) -> None:
    args = parse_args(docopt(__doc__, argv))
    main(**args)
