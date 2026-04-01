from django.db.backends.postgresql.introspection import DatabaseIntrospection as PostgreSQLIntrospection
from django.db.backends.postgresql.introspection import TableInfo


class DatabaseIntrospection(PostgreSQLIntrospection):
    def get_table_list(self, cursor):
        cursor.execute(
            """
            SELECT
                c.relname,
                CASE
                    WHEN c.relkind = 'p' THEN 'p'
                    WHEN c.relkind IN ('m', 'v') THEN 'v'
                    ELSE 't'
                END,
                obj_description(c.oid, 'pg_class')
            FROM pg_catalog.pg_class c
            LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relkind IN ('f', 'm', 'p', 'r', 'v')
                AND n.nspname NOT IN ('pg_catalog', 'pg_toast')
                AND pg_catalog.pg_table_is_visible(c.oid)
            """
        )
        return [
            TableInfo(*row)
            for row in cursor.fetchall()
            if row[0] not in self.ignored_tables
        ]
