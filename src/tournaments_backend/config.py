import logging
import multiprocessing
import os
import tempfile
from typing import Callable, List, Tuple, Any

import yaml


class ConfigSkeleton:
    _parsing_var: dict = {}
    _reverse_var: dict = {}

    _parsing_type: dict = {
        list: lambda v: list(v.split(",")),
        bool: lambda v: bool(v.strip().lower() in ["t", "true", "1"])
    }

    _reverse_type: dict = {
        list: lambda v: str(",".join(v)),
        bool: lambda v: str(v and "TRUE" or "FALSE")
    }

    _config_file: dict
    _config_env: dict

    def __init__(self):
        super().__init__()

        self._config_file = self._parse_config_file()
        self._config_env = self._parse_config_env()

    def __getattribute__(self, name):
        if not name.isupper():
            return super().__getattribute__(name)

        value = getattr(Config, name)
        var_type = type(value)

        if name in self._config_file:
            value = self._config_file[name]
            if name in self._parsing_var:
                value = self._parsing_var[name](value)

        if name in os.environ.keys():
            if name in self._parsing_var:
                fn_conversion = self._parsing_var[name]
            elif var_type in self._parsing_type:
                fn_conversion = self._parsing_type[var_type]
            else:
                fn_conversion = var_type

            return fn_conversion(os.environ[name])

        return value

    def _parse_config_file(self) -> dict:
        conf_file_path: str = os.environ.get("CONFIG_FILE", "config.yml")

        if os.path.exists(conf_file_path):
            with open(conf_file_path, "r") as fd:
                config_file_dict = yaml.safe_load(fd)
                return self._flatten_dict(config_file_dict)

        return dict()

    def _parse_config_env(self) -> dict:
        pass

    def print(self, logging_method: Callable = print, hide_secrets: List[str] = None) -> None:
        if hide_secrets is None:
            hide_secrets = ["PASS", "SECRET"]

        def prepare_var(name: str, value: Any) -> Tuple[str, Any]:
            if any([x in name.upper() for x in hide_secrets]):
                value = "*****"
            return name, value

        var_list: List[Tuple[str, Any]] = [
            prepare_var(name, getattr(self, name)) for name, _ in vars(Config).items()
            if name.isupper()
        ]

        longest_key_size: int = max([len(x[0]) for x in var_list] + [0])
        longest_value_size: int = max([len(str(x[1])) for x in var_list] + [0])
        header_size: int = longest_key_size + longest_value_size + 3

        logging_method("#" * header_size)

        for (var_name, var_value) in var_list:
            var_type = type(var_value)
            value = var_value
            if var_name in self._reverse_var:
                value = self._reverse_var[var_name](value)
            elif var_type in self._reverse_type:
                value = self._reverse_type[var_type](value)
            logging_method(f"{var_name.ljust(longest_key_size, ' ')} : {value}")

        logging_method("#" * header_size)

    @staticmethod
    def _flatten_dict(dictionary, separator="_", prefix=""):
        res = {}
        for key, value in dictionary.items():
            if isinstance(value, dict):
                res.update(
                    Config._flatten_dict(dictionary=value, separator=separator, prefix=f"{prefix}{key}{separator}"))
            else:
                res[f"{prefix}{key}".upper()] = value
        return res


def _compute_dir_path(dir_name: str) -> str:
    project_root: str = os.path.abspath(os.path.join(__file__, "..", "..", ".."))
    dir_path: str = os.path.join(project_root, dir_name)
    if os.path.exists(dir_path):
        return dir_path
    return f"/{dir_name}"


def _compute_dir_path_files() -> str:
    dir_path: str = "/files"
    if os.path.exists(dir_path):
        return dir_path
    return os.path.abspath(tempfile.gettempdir())


class Config(ConfigSkeleton):
    APP_HOST: str = "::"
    APP_PORT: int = 8000
    APP_WORKERS: int = multiprocessing.cpu_count()

    LOG_LEVEL: int = logging.WARNING
    LOG_FORMAT: str = "%(asctime)s,%(msecs)d [%(levelname)07s] [%(process)s|%(thread)s] {%(processName)s} %(funcName)s {%(pathname)s:%(lineno)d}: %(message)s"
    LOG_ACCESS_FORMAT: str = "%(asctime)s - %(client_addr)s - \"%(request_line)s\" %(status_code)s"

    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_USERNAME: str = "tournaments"
    DB_PASSWORD: str = ""
    DB_NAME: str = "tournaments"

    ADDONS_PATH: list[str] = ["odoo/odoo/addons", "odoo/addons", "addons"]
    ADDONS_LIST: list[str] = ["tournaments", "showcases"]

    DATADIR: str = "/data"

    JWT_SIGN_KEY: str = ""
    JWT_ENCRYPT_KEY: str = ""

    _parsing_var: dict = {
        "LOG_LEVEL": lambda v: logging.getLevelName(v)
    }

    _reverse_var: dict = {
        "LOG_LEVEL": lambda v: logging.getLevelName(v)
    }


config = Config()
