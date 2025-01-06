import sqlite3

from db_context.abc_context import DBContext
from dto.article import Article


class SQLiteDBContext(DBContext):
    __db_path: str

    def __init__(self, db_path: str):
        self.__db_path = db_path

    @staticmethod
    def __article_factory(cursor, row):
        fields = [column[0] for column in cursor.description]
        return Article(**{key: value for key, value in zip(fields, row)})

    @staticmethod
    def __single_field_factory(cursor, row):
        return row[0]

    def insert(self, values: tuple[str, str, str, str]) -> None:
        with sqlite3.Connection(self.__db_path) as con:
            con.execute(
                "INSERT INTO Articles (url, title, description, date) VALUES(?, ?, ?, ?)",
                values
            )

    def delete_where_days_limit(self, days_limit: int) -> None:
        with sqlite3.Connection(self.__db_path) as con:
            con.execute(
                "DELETE FROM Articles WHERE julianday(date('now')) - julianday(date) > ?",
                (days_limit,)
            )

    def select_min_date_by_clusters(self) -> list[Article]:
        with sqlite3.Connection(self.__db_path) as con:
            con.row_factory = self.__article_factory
            return con.execute(
                "SELECT cluster_n, title, min(date) as date FROM Articles GROUP BY cluster_n"
            ).fetchall()

    def select_by_cluster(self, cluster_n: int) -> list[Article]:
        with sqlite3.Connection(self.__db_path) as con:
            con.row_factory = self.__article_factory
            return con.execute(
                "SELECT url, title, date FROM Articles WHERE cluster_n = ?",
                (cluster_n,)
            ).fetchall()

    def select_descriptions(self) -> list[str]:
        with sqlite3.connect(self.__db_path) as con:
            con.row_factory = self.__single_field_factory
            return con.execute(
                "SELECT description FROM Articles"
            ).fetchall()

    def set_cluster_n_where_description(self, clusters: list[int], descriptions: list[str]) -> None:
        with sqlite3.connect(self.__db_path) as con:
            con.executemany(
                "UPDATE Articles SET cluster_n = ? WHERE description = ?",
                [
                    (int(cluster_n), description)
                    for description, cluster_n
                    in zip(descriptions, clusters)
                ]
            )