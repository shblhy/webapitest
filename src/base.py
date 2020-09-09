import json
from ._typing import *
from .utils import logger

__all__ = (
    'json', 'Enum', 'dataclass', 'Any', 'Optional', 'List', 'Union', 'Dict', 'TypeVar', 'Callable', 'Type', 'cast', 'T', 'EnumT',
    'from_str', 'from_none', 'from_union', 'to_enum', 'from_list', 'to_class', 'from_bool', 'from_int', 'from_dict',
    'from_float', 'to_float', 'DataClassMixin', 'FileLoaderMixin', 'Case'
)


class DataClassMixin:
    def get_changed_keys(self):
        res = []
        for key in self.__class__.__dict__['__annotations__']:
            if hasattr(self.__class__, key):
                if getattr(self.__class__, key) is not getattr(self, key):
                    res.append(key)
            else:
                res.append(key)
        return res


class FileLoaderMixin:
    @classmethod
    def load_from_file(cls, path):
        logger.info('load scene from file %s' % path)
        f = open(path)
        s = f.read()
        f.close()
        return cls.from_dict(json.loads(s))


@dataclass
class Case(DataClassMixin):
    name: str
    params: dict
    desc: str = None
    response: list = None

    @staticmethod
    def from_dict(obj: Any) -> 'Case':
        name = from_str(obj.get("name"))
        params = dict(obj.get('params'))
        desc = obj.get('desc')
        return Case(name, params, desc)

    def to_dict(self) -> dict:
        result = {}
        result['name'] = self.name
        result['params'] = self.params
        result['desc'] = self.desc
        result['response'] = self.response
        return {k: result[k] for k in result if k in self.get_changed_keys()}

    def get_payload(self):
        return self.params
