"""
Read a PMS5003/PMS7003/PMSA003 sensor and print PM measurements

Usage:
     pms [options]

Options:
    -s, --serial <port>     serial port [default: /ser/ttyUSB0]
    -n, --interval <secs>   seconds to wait between updates [default: 60]
    --csv                   csv formatted output
    -h, --help              display this help and exit

Notes:
- Needs Python 3.7+ for dataclasses
"""

from docopt import docopt
from . import main

args = docopt(__doc__)
try:
    main(interval=int(args["--interval"]), serial=args["--serial"], csv=args["--csv"])
except KeyboardInterrupt:
    print()
except Exception as e:
    print(__doc__)
    print(e)
