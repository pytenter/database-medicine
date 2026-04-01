from django.db.backends.postgresql.base import DatabaseWrapper as PostgreSQLDatabaseWrapper

from .introspection import DatabaseIntrospection


class DatabaseWrapper(PostgreSQLDatabaseWrapper):
    vendor = "postgresql"
    display_name = "openGauss"
    introspection_class = DatabaseIntrospection

    def check_database_version_supported(self):
        return
