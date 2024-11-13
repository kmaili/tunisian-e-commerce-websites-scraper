from prettyconf import Configuration
from prettyconf.loaders import Environment, EnvFile, IniFile
from .loaders import ClassArgs, DefaultConfig
from .utils import mapper
from typing import Dict, Any

import os


class ConfigReader:
    def __init__(self, name="e_commerce_scraper", base_path="./"):
        self.loaders = [
            Environment(var_format=mapper),
            EnvFile(var_format=mapper),
            IniFile(os.path.join(base_path, "drivers.cfg"), section=name),
            IniFile(os.path.join(base_path, "setup.cfg"), section=name),
            DefaultConfig(),
        ]
        self._config = Configuration(self.loaders)

    def __call__(self, item, cast=lambda v: v, **kwargs: Dict[str, Any]):
        return self._config(item, cast=lambda v: v, **kwargs)

    def extend(self, **kwargs: Dict[str, Any]):
        self.loaders.insert(0, ClassArgs(**kwargs))
        self._config = Configuration(self.loaders)

    def free(self):
        self.loaders.pop(0)
        self._config = Configuration(self.loaders)
