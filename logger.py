import json
from abc import ABC, abstractmethod
from logging import getLogger, basicConfig, INFO
from logging.config import dictConfig
from typing import final


class Logger(ABC):
    @staticmethod
    @abstractmethod
    def create_from_config(config_path: str):
        ...

    @abstractmethod
    def info(self, msg: str) -> None:
        ...

    @abstractmethod
    def debug(self, msg: str) -> None:
        ...

    @abstractmethod
    def error(self, msg: str) -> None:
        ...


@final
class SimpleLogger(Logger):
    __logger: Logger

    def __init__(self) -> None:
        self.__logger = getLogger(__name__)
        basicConfig(level=INFO)

    @staticmethod
    def create_from_config(config_path: str) -> Logger:
        try:
            with open(config_path) as file:
                config = json.load(file)

            dictConfig(config)
            return getLogger()

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Ошибка при загрузке: {e.strerror}")

    def info(self, msg: str):
        self.__logger.info(msg)

    def debug(self, msg: str):
        self.__logger.debug(msg)

    def error(self, msg: str):
        self.__logger.error(msg)
