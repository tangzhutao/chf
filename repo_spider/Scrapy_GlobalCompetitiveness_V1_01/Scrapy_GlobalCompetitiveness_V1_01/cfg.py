from pybase.apollo_setting import get_project_settings

config = get_project_settings()

MYSQL_HOST = config.get("MYSQL_HOST")
MYSQL_PORT = config.get("MYSQL_PORT")
MYSQL_USER = config.get("MYSQL_USER")
MYSQL_PASSWORD = config.get("MYSQL_PASSWORD")
MYSQL_DATABASE = config.get("MYSQL_DATABASE")
MYSQL_CHRASET = config.get("MYSQL_CHRASET")
MYSQL_TABLE_REPO = config.get("MYSQL_TABLE_REPO")
MYSQL_TABLE_LOG = config.get('MYSQL_TABLE_LOG')
