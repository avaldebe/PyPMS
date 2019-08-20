"""
Read a PMS5003/PMS7003/PMSA003 sensor and push PM measurements to a MQTT server

Usage:
    pms.mqtt [options]

Options:
    --topic <topic>         MQTT topic [default: aqmon/test]
    --host <host>           MQTT host server [default: test.mosquitto.org]
    --port <port>           MQTT host port [default: 1883]
    --user <username>       MQTT username
    --pass <password>       MQTT password

Other:
    -s, --serial <port>     serial port [default: /dev/ttyUSB0]
    -n, --interval <secs>   seconds to wait between updates [default: 60]
    -h, --help              display this help and exit

Notes:
- Needs Python 3.7+ for dataclasses
- Only partial support for Homie v2.0.0 MQTT convention 
  https://homieiot.github.io/specification/spec-core-v2_0_0/
"""

from docopt import docopt
from . import main

args = docopt(__doc__)
try:
    main(
        interval=int(args["--interval"]),
        serial=args["--serial"],
        host=args["--host"],
        port=args["--port"],
        username=args["--user"],
        password=args["--pass"],
        topic=args["--topic"],
    )
except KeyboardInterrupt:
    print()
except Exception as e:
    print(__doc__)
    print(e)
