from dataclasses import dataclass
from datetime import datetime


@dataclass
class Article:
    url: str = None
    title: str = None
    description: str = None
    date: datetime = None
    cluster_n: int = None
