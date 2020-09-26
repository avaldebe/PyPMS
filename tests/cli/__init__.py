from enum import Enum
from datetime import datetime
from typing import NamedTuple, Dict, List, Generator, Optional

from pms.sensor import Sensor, base


class Obs(NamedTuple):
    """Captured sensor data, single observation"""

    hex: str
    csv: str

    @property
    def raw(self) -> bytes:
        return bytes.fromhex(self.hex)

    @property
    def time(self) -> int:
        return int(self.csv.split(",")[0].strip())

    def decode(self, sensor: Sensor) -> base.ObsData:
        return sensor.decode(self.raw, time=self.time)


class CapturedData(Enum):

    PMSx003 = (  # pms -m PMSx003 -n 5 -i 10 serial -f csv
        Obs(
            "424d001c00000008000b00000008000b00b40039002e001e00000000970002a1",
            "1601120880, 0, 8, 11, 0.0, 8.0, 11.0, 1.80, 0.57, 0.46, 0.30, 0.00, 0.00",
        ),
        Obs(
            "424d001c000000080008000000080008011d005c001e001e0000000097000218",
            "1601120890, 0, 8, 8, 0.0, 8.0, 8.0, 2.85, 0.92, 0.30, 0.30, 0.00, 0.00",
        ),
        Obs(
            "424d001c0000000500050000000500050024000c000c000c000000009700019e",
            "1601120900, 0, 5, 5, 0.0, 5.0, 5.0, 0.36, 0.12, 0.12, 0.12, 0.00, 0.00",
        ),
        Obs(
            "424d001c000000020004000000020004001e000a000300030003000397000182",
            "1601120910, 0, 2, 4, 0.0, 2.0, 4.0, 0.30, 0.10, 0.03, 0.03, 0.03, 0.03",
        ),
        Obs(
            "424d001c00000000000100000000000100120006000300030003000397000168",
            "1601120920, 0, 0, 1, 0.0, 0.0, 1.0, 0.18, 0.06, 0.03, 0.03, 0.03, 0.03",
        ),
    )

    @property
    def samples(self) -> int:
        return len(self.value)

    @property
    def interval(self) -> int:
        return 10

    @property
    def options(self) -> Dict[str, List[str]]:
        capture = f"-m {self.name} -s {self.samples} -i {self.interval}"
        return dict(
            serial=f"{capture} serial -f csv".split(),
            csv=f"{capture} csv --overwrite -F test.csv".split(),
            mqtt=f"{capture} mqtt".split(),
            influxdb=f"{capture} influxdb".split(),
        )

    @property
    def csv(self) -> str:
        heder = dict(
            PMSx003="time, raw01, raw25, raw10, pm01, pm25, pm10, n0_3, n0_5, n1_0, n2_5, n5_0, n10_0",
        )[self.name]
        csv = "\n".join(obs.csv for obs in self.value)
        return f"{heder}\n{csv}\n"


class MockReader:
    """mock pms.sensor.SensorReader"""

    def __init__(
        self, sensor: str, port: str, interval: int, samples: Optional[int] = None
    ) -> None:
        try:
            self.sensor = Sensor[sensor]
        except KeyError:
            raise ValueError(f"unknown sensor '{sensor}'")

        try:
            self.data = CapturedData[sensor]
        except KeyError:
            raise NotImplementedError(f"missing captured data to test {sensor} sensor")

        if samples and samples > self.data.samples:
            raise ValueError(f"not enough captured data to test {sensor} sensor")

    def __enter__(self) -> "MockReader":
        return self

    def __exit__(self, exception_type, exception_value, traceback) -> None:
        pass

    def __call__(self) -> Generator[base.ObsData, None, None]:
        for obs in self.data.value:
            yield obs.decode(self.sensor)