from csv import DictReader
from enum import Enum
from pathlib import Path
from typing import NamedTuple, Dict, List, Tuple, Generator, Optional

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

    @classmethod
    def from_csv(cls, path: Path) -> Tuple["Obs", ...]:
        with path.open() as csv:
            reader = DictReader(csv, delimiter=";")
            return tuple(cls(**row) for row in reader)


class CapturedData(Enum):
    """Captured data from /docs/sensors"""

    PMS3003 = Obs.from_csv(Path("tests/cli/captured_data/PMS3003.csv"))
    PMSx003 = Obs.from_csv(Path("tests/cli/captured_data/PMSx003.csv"))
    SDS01x = Obs.from_csv(Path("tests/cli/captured_data/SDS01x.csv"))
    SDS198 = Obs.from_csv(Path("tests/cli/captured_data/SDS198.csv"))
    MCU680 = Obs.from_csv(Path("tests/cli/captured_data/MCU680.csv"))

    @property
    def samples(self) -> int:
        return len(self.value) - 2

    @property
    def interval(self) -> int:
        return 10

    @property
    def options(self) -> Dict[str, List[str]]:
        capture = f"-m {self.name} -s {self.samples} -i {self.interval}"
        return dict(
            serial=f"{capture} serial -f csv".split(),
            csv=f"{capture} csv --overwrite {self.name}_test.csv".split(),
            capture=f"{capture} csv --capture {self.name}_pypms.csv".split(),
            raw=f"{capture} raw".split(),
            decode=f"{capture} raw --decode --test-file {self.name}_pypms.csv".split(),
            mqtt=f"{capture} mqtt".split(),
            influxdb=f"{capture} influxdb".split(),
        )

    @property
    def csv(self) -> str:
        heder = self.value[1].csv
        csv = "\n".join(obs.csv for obs in self.value[2:])
        return f"{heder}\n{csv}\n"

    @property
    def hex(self) -> str:
        hex = "\n".join(obs.hex for obs in self.value[2:])
        return f"{hex}\n"


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

    def __call__(self, *, raw: bool = False) -> Generator[base.ObsData, None, None]:
        for obs in self.data.value[2:]:
            yield obs.raw if raw else obs.decode(self.sensor)
