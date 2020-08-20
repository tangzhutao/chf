# import pymysql
# import time
# from pymysql.cursors import DictCursor
# from pybase.apollo_setting import get_project_settings
#
# settings = get_project_settings()
#
# MYSQL_HOST = settings.get("MYSQL_HOST")
# MYSQL_USER = settings.get("MYSQL_USER")
# MYSQL_PASSWORD = settings.get("MYSQL_PASSWORD")
# MYSQL_DATABASE = settings.get("MYSQL_DATABASE")
# MYSQL_TABLE = settings.get("MYSQL_TABLE")
# MYSQL_TABLE_LOG = settings.get('MYSQL_TABLE_LOG')
# # MYSQL_TABLE = settings.get("MYSQL_TABLE_TEST")
#
# # MYSQL_HOST = '192.168.0.39'
# # MYSQL_USER = 'root'
# # MYSQL_PASSWORD = 'root'
# # MYSQL_DATABASE = 'js'
# # # MYSQL_TABLE = settings.get("MYSQL_TABLE")
# # MYSQL_TABLE = 'd44_data_new'
#
#
# # 连接数据库
# def connet():
#     db = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE)
#     cursor = db.cursor(DictCursor)
#     return db, cursor
#
#
# # 菜单：检查数据库是否有表，没有就建表
# def check_table():
#     db, cursor = connet()
#     sql = "show tables"
#     cursor.execute(sql)
#     table_list = [item[key] for item in cursor.fetchall() for key in item]
#     if MYSQL_TABLE not in table_list:
#         create = "CREATE TABLE %s(menu_id VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,menu_name VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, parent_menu_id VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, isRep VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, PRIMARY KEY (menu_id))" % (
#             MYSQL_TABLE)
#         cursor.execute(create)
#     db.close()
#
#
# # 菜单：获取该节点的数量
# def select_count(parent_id):
#     db, cursor = connet()
#     sql = "SELECT * FROM %s where parent_menu_id = '%s'" % (MYSQL_TABLE, parent_id)
#     # print(sql)
#     count = cursor.execute(sql)
#     # print(count)
#     cursor.close()
#     db.close()
#
#     return count
#
#
# # 菜单：判断是否有重复
# def select(menu_name, parent_menu_id, isRep):
#     db, cursor = connet()
#     sql = "SELECT * FROM %s where menu_name = '%s' and parent_menu_id = '%s' and isRep = '%s'" % (
#         MYSQL_TABLE, menu_name, parent_menu_id, isRep)
#     # print(sql)
#     count = cursor.execute(sql)
#     a = cursor.fetchone()
#     cursor.close()
#     db.close()
#     return a
#
#
# # 菜单：插入菜单
# def insert(menu_id, menu_name, parent_id, isRep):
#     db, cursor = connet()
#     try:
#         # 这种方式可解决验证问题
#         sql = "insert into %s(menu_id, menu_name, parent_menu_id, isRep) values('%s','%s','%s','%s')" % (
#             MYSQL_TABLE, menu_id, menu_name, parent_id, isRep)
#         info = cursor.execute(sql)
#         db.commit()
#         cursor.close()
#         db.close()
#         return info
#     except Exception as e:
#         # print(e)
#         db.rollback()
#
#
# # 账号：获取账号密码
# def get_cookie():
#     db, cursor = connet()
#     sql = "select * from robo_cookie_chf"
#     cursor.execute(sql)
#     while True:
#         user_pwd = cursor.fetchone()
#         if not user_pwd['state']:
#             break
#     cursor.close()
#     db.close()
#     return user_pwd
#
#
# # 账号：修改账号状态
# def change_state(cookie):
#     db, cursor = connet()
#     try:
#         sql2 = "UPDATE robo_cookie_chf SET state = 1 WHERE usr = '%s'" % (cookie['usr'])
#         cursor.execute(sql2)
#         db.commit()
#     except IndexError:
#         db.rollback()
#     cursor.close()
#     db.close()
#
#
# # 账号：恢复账号状态
# def restore(cookie):
#     db, cursor = connet()
#     try:
#         sql2 = "UPDATE robo_cookie_chf SET state = 0 WHERE usr = '%s' and last_time = '%s'" % (
#             cookie['usr'], time.time())
#         cursor.execute(sql2)
#         db.commit()
#     except IndexError:
#         db.rollback()
#
#     cursor.close()
#     db.close()
#
#
# # 日志：记录数据、菜单新增量
# def SpiderLog(project, spider_name, update_time, count, menu_count, url, url_name):
#     db, cursor = connet()
#
#     try:
#         sql = "insert into %s(project, spider_name, update_time, count, menu_count, url, url_name) values('%s','%s','%s','%s','%s','%s','%s')" % (
#             MYSQL_TABLE_LOG, project, spider_name, update_time, count, menu_count, url, url_name)
#         cursor.execute(sql)
#         db.commit()
#     except Exception as e:
#         print(e)
#         db.rollback()
#     cursor.close()
#     db.close()
#
#
# # 日志：记录菜单新增量
# def menu_count():
#     db, cursor = connet()
#     sql = "select * from %s" % (MYSQL_TABLE)
#     count = cursor.execute(sql)
#     cursor.close()
#     db.close()
#     return count
#
#
# if __name__ == '__main__':
#     a = menu_count()
#     print(a)
