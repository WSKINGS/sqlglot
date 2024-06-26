from tests.dialects.test_dialect import Validator


class TestMaterialize(Validator):
    dialect = "materialize"

    def test_materialize(self):
        self.validate_all(
            "CREATE TABLE example (id INT PRIMARY KEY, name TEXT)",
            write={
                "materialize": "CREATE TABLE example (id INT, name TEXT)",
                "postgres": "CREATE TABLE example (id INT PRIMARY KEY, name TEXT)",
            },
        )
        self.validate_all(
            "INSERT INTO example (id, name) VALUES (1, 'Alice') ON CONFLICT(id) DO NOTHING",
            write={
                "materialize": "INSERT INTO example (id, name) VALUES (1, 'Alice')",
                "postgres": "INSERT INTO example (id, name) VALUES (1, 'Alice') ON CONFLICT(id) DO NOTHING",
            },
        )
        self.validate_all(
            "CREATE TABLE example (id SERIAL, name TEXT)",
            write={
                "materialize": "CREATE TABLE example (id INT NOT NULL, name TEXT)",
                "postgres": "CREATE TABLE example (id INT GENERATED BY DEFAULT AS IDENTITY NOT NULL, name TEXT)",
            },
        )
        self.validate_all(
            "CREATE TABLE example (id INT AUTO_INCREMENT, name TEXT)",
            write={
                "materialize": "CREATE TABLE example (id INT NOT NULL, name TEXT)",
                "postgres": "CREATE TABLE example (id INT GENERATED BY DEFAULT AS IDENTITY NOT NULL, name TEXT)",
            },
        )
        self.validate_all(
            'SELECT JSON_EXTRACT_PATH_TEXT(\'{ "farm": {"barn": { "color": "red", "feed stocked": true }}}\', \'farm\', \'barn\', \'color\')',
            write={
                "materialize": 'SELECT JSON_EXTRACT_PATH_TEXT(\'{ "farm": {"barn": { "color": "red", "feed stocked": true }}}\', \'farm\', \'barn\', \'color\')',
                "postgres": 'SELECT JSON_EXTRACT_PATH_TEXT(\'{ "farm": {"barn": { "color": "red", "feed stocked": true }}}\', \'farm\', \'barn\', \'color\')',
            },
        )
        self.validate_all(
            "SELECT MAP['a' => 1]",
            write={
                "duckdb": "SELECT MAP {'a': 1}",
                "materialize": "SELECT MAP['a' => 1]",
            },
        )

        # Test now functions.
        self.validate_identity("CURRENT_TIMESTAMP")
        self.validate_identity("NOW()", write_sql="CURRENT_TIMESTAMP")
        self.validate_identity("MZ_NOW()")

        # Test custom timestamp type.
        self.validate_identity("SELECT CAST(1 AS mz_timestamp)")

        # Test DDL.
        self.validate_identity("CREATE TABLE example (id INT, name LIST)")

        # Test list types.
        self.validate_identity("SELECT LIST[]")
        self.validate_identity("SELECT LIST[1, 2, 3]")
        self.validate_identity("SELECT LIST[LIST[1], LIST[2], NULL]")
        self.validate_identity("SELECT CAST(LIST[1, 2, 3] AS INT LIST)")
        self.validate_identity("SELECT CAST(NULL AS INT LIST)")
        self.validate_identity("SELECT CAST(NULL AS INT LIST LIST LIST)")
        self.validate_identity("SELECT LIST(SELECT 1)")

        # Test map types.
        self.validate_identity("SELECT MAP[]")
        self.validate_identity("SELECT MAP['a' => MAP['b' => 'c']]")
        self.validate_identity("SELECT CAST(MAP['a' => 1] AS MAP[TEXT => INT])")
        self.validate_identity("SELECT CAST(NULL AS MAP[TEXT => INT])")
        self.validate_identity("SELECT CAST(NULL AS MAP[TEXT => MAP[TEXT => INT]])")
        self.validate_identity("SELECT MAP(SELECT 'a', 1)")
