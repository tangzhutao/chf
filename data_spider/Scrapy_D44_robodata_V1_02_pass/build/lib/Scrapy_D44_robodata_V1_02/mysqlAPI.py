import pymysql
import time
from pymysql.cursors import DictCursor
from pybase.apollo_setting import get_project_settings

settings = get_project_settings()

MYSQL_HOST = settings.get("MYSQL_HOST")
MYSQL_USER = settings.get("MYSQL_USER")
MYSQL_PASSWORD = settings.get("MYSQL_PASSWORD")
MYSQL_DATABASE = settings.get("MYSQL_DATABASE")
MYSQL_TABLE = settings.get("MYSQL_TABLE")
# MYSQL_TABLE = settings.get("MYSQL_TABLE_TEST")

# MYSQL_HOST = '192.168.0.39'
# MYSQL_USER = 'root'
# MYSQL_PASSWORD = 'root'
# MYSQL_DATABASE = 'js'
# # MYSQL_TABLE = settings.get("MYSQL_TABLE")
# MYSQL_TABLE = 'd44_data_new'


def connet():
    db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)

    cursor = db.cursor(DictCursor)

    return db, cursor


# 检查数据库是否有表，没有就建表
def check_table():
    db, cursor = connet()
    sql = "show tables"
    cursor.execute(sql)
    table_list = [item[key] for item in cursor.fetchall() for key in item]
    if MYSQL_TABLE not in table_list:
        create = "CREATE TABLE %s(menu_id VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,menu_name VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, parent_menu_id VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, isRep VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, PRIMARY KEY (menu_id))" % (
            MYSQL_TABLE)
        cursor.execute(create)
    db.close()
    # return table_list


# 获取该节点的数量
def select_count(parent_id):
    db, cursor = connet()

    sql = "SELECT * FROM %s where parent_menu_id = '%s'" % (MYSQL_TABLE, parent_id)
    # print(sql)
    count = cursor.execute(sql)
    # print(count)
    cursor.close()
    db.close()

    return count


# 判断是否有重复
def select(menu_name, parent_menu_id, isRep):
    db, cursor = connet()
    sql = "SELECT * FROM %s where menu_name = '%s' and parent_menu_id = '%s' and isRep = '%s'" % (
    MYSQL_TABLE, menu_name, parent_menu_id, isRep)
    # print(sql)
    count = cursor.execute(sql)
    a = cursor.fetchone()
    cursor.close()
    db.close()
    return a


def insert(menu_id, menu_name, parent_id, isRep):
    db, cursor = connet()
    try:
        # 这种方式可解决验证问题
        sql = "insert into %s(menu_id, menu_name, parent_menu_id, isRep) values('%s','%s','%s','%s')" % (
        MYSQL_TABLE, menu_id, menu_name, parent_id, isRep)
        # print(sql)
        info = cursor.execute(sql)
        # print(info)
        db.commit()
        cursor.close()
        db.close()
        return info
    except Exception as e:
        # print(e)
        db.rollback()


def get_cookie():
    db = pymysql.connect('192.168.0.11', 'root', '123456', 'wgf_catalog')
    cursor = db.cursor(DictCursor)
    sql = "select * from robo_cookie_chf"
    cursor.execute(sql)
    while True:
        user_pwd = cursor.fetchone()
        print(user_pwd['state'])
        if not user_pwd['state']:
            break
    cursor.close()
    db.close()
    return user_pwd


def change_state(cookie):
    db = pymysql.connect('192.168.0.11', 'root', '123456', 'wgf_catalog')
    cursor = db.cursor(DictCursor)
    try:
        sql2 = "UPDATE robo_cookie_chf SET state = 1 WHERE usr = '%s'" % (cookie['usr'])
        cursor.execute(sql2)
        db.commit()
    except:
        db.rollback()

    cursor.close()
    db.close()


def restore(cookie):
    db = pymysql.connect('192.168.0.11', 'root', '123456', 'wgf_catalog')
    cursor = db.cursor(DictCursor)
    last_time = time.time()
    try:
        sql2 = "UPDATE robo_cookie_chf SET state = 0 WHERE usr = '%s' and last_time = '%s'" % (cookie['usr'], last_time)
        cursor.execute(sql2)
        db.commit()
    except:
        db.rollback()

    cursor.close()
    db.close()


if __name__ == '__main__':
    check_table()
    parent_id = '5001000001'
    title = '行业经济>房地产及建筑业>土地交易数据库:城市>土地交易数据库:城市(季)>四川>土地交易统计:成都市(季)'
    id = '50000011'
    menu = '测试菜单'
    p_id = '000'
    isRep = 'A01'
    a = select_count(parent_id)
    print(a)
    b = insert(id, menu, p_id, isRep)
    print(b)
    # c = select(title)
    # print(type(a), a, b, c)
