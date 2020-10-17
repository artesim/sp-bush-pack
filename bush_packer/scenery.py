from __future__ import annotations  # Allow forward reference type annotation in py3.8

import typing

from dataclasses import dataclass
from pathlib import Path

if typing.TYPE_CHECKING:
    from typing import List


@dataclass(frozen=True)
class Scenery:
    scenery_id: str
    src_dir: Path

    @classmethod
    def load(cls, src_dir: Path) -> Scenery:
        scenery_id = src_dir.name
        return Scenery(scenery_id=scenery_id,
                       src_dir=src_dir)

    def build(self, out_dir: Path) -> List[Path]:
        return list()

    def dump_xml(self) -> str:
        return ''
