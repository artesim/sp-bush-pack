from __future__ import annotations  # Allow forward reference type annotation in py3.8

import collections
import uuid

from dataclasses import dataclass
from enum import Enum
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    pass


class Lang(Enum):
    EN_US = 'en-US'
    FR_FR = 'fr-FR'
    DEFAULT = EN_US


@dataclass(frozen=True)
class LocTuple:
    lang: Lang
    str: str


class LocStr:
    __instances__: Dict[str, LocStr] = dict()

    def __new__(cls, *, str_id: str, alternatives: Dict[Lang, str]):
        if str_id not in cls.__instances__:
            instance = super().__new__(cls)
            instance.str_id = str_id
            instance.alternatives = alternatives
            cls.__instances__[str_id] = instance
        return cls.__instances__[str_id]

    def __str__(self):
        return f'TT:{self.str_id}'

    def __getitem__(self, item: Lang):
        return self.alternatives.get(item)

    @classmethod
    def dump_instances(cls) -> dict:
        loc_packs = collections.defaultdict(dict)
        for instance in cls.__instances__.values():
            for lang, translation in instance.alternatives.items():
                loc_packs[lang][instance.str_id] = translation
        return loc_packs


def new_uuid_str() -> str:
    return '{' + str(uuid.uuid1()).upper() + '}'
