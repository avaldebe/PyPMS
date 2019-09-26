from invoke import task
from pms import PMSerial, logger


@task(
    name="serial",
    help={
        "serial": "serial port [default: /dev/ttyUSB0]",
        "interval": "seconds to wait between updates [default: 60]",
        "format": "(pm|num|csv)formatted output  [default: pm]",
        "debug": "print DEBUG/logging messages",
    },
)
def main(context, serial="/dev/ttyUSB0", interval=60, format="pm", debug=False):
    """Read PMSx003 sensor and print PM measurements"""
    if debug:
        logger.setLevel("DEBUG")
    try:
        with PMSerial(serial) as read:
            for pm in read(interval):
                print(f"{pm:{format}}")
    except KeyboardInterrupt:
        print()
    except Exception as e:
        logger.exception(e)
