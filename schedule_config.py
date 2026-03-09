from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

import polars as pl
import yaml


@dataclass
class ScheduleConfig:
    name: str
    weeks_csv: str
    residents_csv: str
    rotations_yaml: Optional[str] = None
    rotations_csv: Optional[str] = None
    requirements: Dict[str, str] = field(default_factory=dict)
    manual_overrides: Dict = field(default_factory=dict)

    def get_rotations_df(self) -> pl.DataFrame:
        if self.rotations_yaml:
            from rotation_builder import RotationBuilder

            builder = RotationBuilder.from_yaml(self.rotations_yaml)
            return builder.to_polars()
        elif self.rotations_csv:
            return pl.read_csv(self.rotations_csv)
        else:
            raise ValueError("No rotations source specified")

    def get_weeks_df(self) -> pl.DataFrame:
        return pl.read_csv(self.weeks_csv, try_parse_dates=True)

    def get_residents_df(self) -> pl.DataFrame:
        return pl.read_csv(self.residents_csv)

    def get_requirements_for_type(self, resident_type: str) -> dict:
        req_path = self.requirements.get(resident_type)
        if not req_path:
            return {}

        req_file = Path(req_path)
        if not req_file.is_absolute():
            config_dir = Path(self._config_path).parent
            req_file = config_dir / req_path

        with open(req_file, "r") as f:
            import box

            return box.Box(yaml.safe_load(f))

    @classmethod
    def from_yaml(cls, path: str) -> "ScheduleConfig":
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        config = cls(
            name=data.get("name", ""),
            weeks_csv=data["weeks_csv"],
            residents_csv=data["residents_csv"],
            rotations_yaml=data.get("rotations_yaml"),
            rotations_csv=data.get("rotations_csv"),
            requirements=data.get("requirements", {}),
            manual_overrides=data.get("manual_overrides", {}),
        )
        config._config_path = path
        return config

    def to_yaml(self, path: str) -> None:
        data = {
            "name": self.name,
            "weeks_csv": self.weeks_csv,
            "residents_csv": self.residents_csv,
        }
        if self.rotations_yaml:
            data["rotations_yaml"] = self.rotations_yaml
        if self.rotations_csv:
            data["rotations_csv"] = self.rotations_csv
        if self.requirements:
            data["requirements"] = self.requirements
        if self.manual_overrides:
            data["manual_overrides"] = self.manual_overrides

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def load_schedule_config(path: str) -> ScheduleConfig:
    return ScheduleConfig.from_yaml(path)
