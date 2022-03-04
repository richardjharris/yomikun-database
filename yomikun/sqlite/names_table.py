import romkan
from yomikun.sqlite.constants import PART_ID, SqliteQuery


class NamesTable:
    """
    Class for generating the `names` table, which is the main table
    for all name reading and hit count data.
    """

    def make_query(self, row: dict) -> SqliteQuery:
        values = (
            row["kaki"],
            romkan.to_roma(row["yomi"]),
            PART_ID[row["part"]],
            row["hits_total"],
            row["hits_male"],
            row["hits_female"],
            row["hits_pseudo"],
            row.get("ml_score", 0),
        )

        return (
            f"""
                INSERT INTO names(kaki,yomi,part,hits_total,hits_male,hits_female,hits_pseudo,ml_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            values,
        )

    @staticmethod
    def create_statement() -> str:
        return """
            CREATE TABLE names(
                kaki TEXT,
                yomi TEXT, -- in romaji (saves 15% db size over kana)
                part INT,  -- 0=unknown 1=sei 2=mei (saves 15% over string)
                hits_total INT,
                hits_male INT,
                hits_female INT,
                hits_pseudo INT,
                ml_score INT,
                PRIMARY KEY (kaki, yomi, part, hits_total DESC)
            );
            CREATE INDEX names_yomi ON names (yomi, part, hits_total DESC);
        """