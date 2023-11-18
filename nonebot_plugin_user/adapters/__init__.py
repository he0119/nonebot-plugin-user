from typing import Dict

from ..extractor import Extractor
from .qq import QQExtractor  # noqa: F401

MAPPING: Dict[str, Extractor] = {
    cls.get_adapter(): cls() for cls in Extractor.__subclasses__()
}
