from prettyconf.loaders import AbstractConfigurationLoader
from . import defaults
from typing import Dict, Any


class ClassArgs(AbstractConfigurationLoader):
    def __init__(self, **kwargs: Dict[str, Any]):
        self.configs = kwargs

    def __repr__(self):
        return "ClassArgs"

    def __contains__(self, item):
        return item in self.configs

    def __getitem__(self, item):
        return self.configs[item]


class DefaultConfig(AbstractConfigurationLoader):
    def __init__(
        self,
    ):
        pass

    def __repr__(self):
        return "DefaultConfig"

    def __contains__(self, item):
        return item in dict(defaults)

    def __getitem__(self, item):
        try:
            return getattr(defaults, item)
        except AttributeError:
            return ""
