"""
Read a PMS5003/PMS7003/PMSA003 sensor and print PM measurements

Usage:
     pms.serial [options]

Options:
    -s, --serial <port>     serial port [default: /dev/ttyUSB0]
    -n, --interval <secs>   seconds to wait between updates [default: 60]
    --csv                   csv formatted output
    -h, --help              display this help and exit
"""

import time
from typing import Dict
from . import read, logger


def parse_args(args: Dict) -> Dict:
    return dict(
        interval=int(args["--interval"]), serial=args["--serial"], csv=args["--csv"]
    )


def main(interval: int, serial: str, csv: bool) -> None:
    for pm in read(serial):
        if csv:
            print(pm.csv())
        else:
            print(pm)

        delay = int(interval) - (time.time() - pm.time)
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
        print(__doc__)
        logger.exception(e)
