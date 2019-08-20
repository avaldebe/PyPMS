"""
Read a PMS5003/PMS7003/PMSA003 sensor and push PM measurements to an InfluxDB server

Usage:
    pms.influxdb [options]

Options:
    --location <tag>        location tag [default: test]
    --host <host>           InfluxDB host server [default: influxdb]
    --port <port>           InfluxDB host port [default: 8086]
    --user <username>       InfluxDB username [default: root]
    --pass <password>       InfluxDB password [default: root]

Other:
    -s, --serial <port>     serial port [default: /dev/ttyUSB0]
    -n, --interval <secs>   seconds to wait between updates [default: 60]
    -h, --help              display this help and exit
"""

from docopt import docopt
from . import main

args = docopt(__doc__)
try:
    main(
        interval=int(args["--interval"]),
        serial=args["--serial"],
        location=args["--location"],
        host=args["--host"],
        port=args["--port"],
        username=args["--user"],
        password=args["--pass"],
    )
except KeyboardInterrupt:
    print()
except Exception as e:
    print(__doc__)
    print(e)
