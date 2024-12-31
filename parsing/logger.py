from abc import ABC, abstractmethod
from logging import getLogger, basicConfig, INFO
from typing import final


class Logger(ABC):
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

    def info(self, msg: str):
        self.__logger.info(msg)

    def debug(self, msg: str):
        self.__logger.debug(msg)

    def error(self, msg: str):
        self.__logger.error(msg)
