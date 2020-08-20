from pybase.apollo_setting import get_project_settings

config = get_project_settings()

MYSQL_HOST = config.get("MYSQL_HOST")
MYSQL_PORT = config.get("MYSQL_PORT")
MYSQL_USER = config.get("MYSQL_USER")
MYSQL_PASSWORD = str(config.get("MYSQL_PASSWORD"))
MYSQL_DATABASE = config.get("MYSQL_DATABASE")
MYSQL_CHRASET = config.get("MYSQL_CHRASET")
MYSQL_TABLE_DATA = config.get("MYSQL_TABLE_DATA")
MYSQL_TABLE_COOKIE = config.get("MYSQL_TABLE_COOKIE")
MYSQL_TABLE_LOG = config.get('MYSQL_TABLE_LOG')

MONGO_URI = config.get("MONGO_URI")
MONGO_DB = config.get("MONGO_NATIONAL_CONDITIONS")
MONGO_COLLECTION = config.get("MONGO_COLLECTION_INFO")

# 图片储存
IMAGES_STORE = config.get("IMAGES_STORE")
SPIDER_NAME = config.get("SPIDER_NAME")
UPLOADURL = config.get("UPLOADURL")


if __name__ == '__main__':
    print(MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_CHRASET, MYSQL_TABLE_DATA,
          MYSQL_TABLE_COOKIE, MYSQL_TABLE_LOG)
    print(MONGO_URI, MONGO_DB, MONGO_COLLECTION)
    print(IMAGES_STORE, SPIDER_NAME, UPLOADURL)
