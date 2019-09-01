"""
Read a PMS5003/PMS7003/PMSA003 sensor and print PM measurements

Usage:
     pms.serial [options]

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
import time
from typing import Dict, Union, Any
from . import read, logger


def parse_args(args: Dict[str, Union[str, bool]]) -> Dict[str, Any]:
    return dict(
        interval=int(os.environ.get("PMS_INTERVAL", args["--interval"])),
        serial=os.environ.get("PMS_SERIAL", args["--serial"]),
        format=os.environ.get("PMS_FORMAT", args["--format"]),
    )


def main(interval: int, serial: str, format: bool) -> None:
    for pm in read(serial):
        print(f"{pm:{format}}")

        delay = interval - (time.time() - pm.time)
        if delay > 0:
            time.sleep(delay)


if __name__ == "__main__":
    from docopt import docopt

    args = parse_args(docopt(__doc__))
    try:
        main(**args)
    except KeyboardInterrupt:
        print()
    except Exception as e:
        logger.exception(e)
