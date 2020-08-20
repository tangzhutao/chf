# -*- coding: UTF-8 -*-
"""
1、执行带参数的ＳＱＬ时，请先用sql语句指定需要输入的条件列表，然后再用tuple/list进行条件批配
２、在格式ＳＱＬ中不需要使用引号指定数据类型，系统会根据输入参数自动识别
３、在输入的值中不需要使用转意函数，系统会自动处理
"""

import pymysql
import time
from pymysql.cursors import DictCursor
from DBUtils.PooledDB import PooledDB
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


class MysqlPool(object):
    """
    MYSQL数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现获取连接对象：conn = Mysql.getConn()
            释放连接对象;conn.close()或del conn
    """
    # 连接池对象
    __pool = None

    def __init__(self):
        # 数据库构造函数，从连接池中取出连接，并生成操作游标
        self._conn = MysqlPool.__getConn()
        self._cursor = self._conn.cursor()

    @staticmethod
    def __getConn():
        """
        @summary: 静态方法，从连接池中取出连接
        @return MySQLdb.connection
        """
        if MysqlPool.__pool is None:
            __pool = PooledDB(creator=pymysql, mincached=3, maxcached=20,
                              host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PASSWORD,
                              db=MYSQL_DATABASE, use_unicode=True, charset=MYSQL_CHRASET, cursorclass=DictCursor)
        return __pool.connection()

    # 检查数据库表
    def check_table(self):
        sql = "show tables"
        self._cursor.execute(sql)
        table_list = [item[key] for item in self._cursor.fetchall() for key in item]
        if MYSQL_TABLE_DATA not in table_list:
            create = "CREATE TABLE %s(menu_id VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,menu_name VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, parent_menu_id VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, isRep VARCHAR(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL, PRIMARY KEY (menu_id))" % (
                MYSQL_TABLE_DATA)
            self._cursor.execute(create)

    # 获取该节点的数量
    def select_count(self, parent_id):
        sql = "SELECT * FROM %s where parent_menu_id = '%s'" % (MYSQL_TABLE_DATA, parent_id)
        count = self._cursor.execute(sql)
        return count

    # 判断是否有重复
    def select(self, menu_name, parent_menu_id, isRep):
        sql = "SELECT * FROM %s where menu_name = '%s' and parent_menu_id = '%s' and isRep = '%s'" % (
            MYSQL_TABLE_DATA, menu_name, parent_menu_id, isRep)
        count = self._cursor.execute(sql)
        result = self._cursor.fetchone()
        return result

    # 插入菜单
    def insert(self, menu_id, menu_name, parent_id, isRep):
        try:
            # 这种方式可解决验证问题
            sql = "insert into %s(menu_id, menu_name, parent_menu_id, isRep) values('%s','%s','%s','%s')" % (
                MYSQL_TABLE_DATA, menu_id, menu_name, parent_id, isRep)
            info = self._cursor.execute(sql)
            self._conn.commit()
            return info
        except Exception as e:
            self._conn.rollback()

    # 获取萝卜投研账号,并修改状态
    def get_cookie(self):
        sql = "select * from %s where state = 0" % (MYSQL_TABLE_COOKIE)
        self._cursor.execute(sql)
        cookie = self._cursor.fetchone()
        return cookie

    # 修改账号状态
    def change_state(self, cookie):
        try:
            sql2 = "update %s set state = 1 where phonenumber = '%s'" % (MYSQL_TABLE_COOKIE, cookie['phonenumber'])
            self._cursor.execute(sql2)
            self._conn.commit()
        except Exception as e:
            print(e)
            self._conn.rollback()

    # 使用结束恢复账号状态
    def restore(self, cookie):
        last_time = str(int(time.time() * 1000))

        try:
            sql = "UPDATE %s SET state = 0, last_time = '%s' where phonenumber = '%s'" % (
                MYSQL_TABLE_COOKIE, last_time, cookie['phonenumber'])
            self._cursor.execute(sql)
            self._conn.commit()
        except Exception as e:
            print(e)
            self._conn.rollback()

    # 日志：记录资讯新增量
    def SpiderLog(self, project, spider_name, update_time, count, menu_count, url, url_name):
        try:
            sql = "insert into %s(project, spider_name, update_time, count, menu_count, url, url_name) values('%s','%s','%s','%s','%s','%s','%s')" % (
                MYSQL_TABLE_LOG, project, spider_name, update_time, count, menu_count, url, url_name)
            self._cursor.execute(sql)
            self._conn.commit()
        except Exception as e:
            print(e)
            self._conn.rollback()

    # 日志：查询菜单数量
    def menu_count(self):
        sql = "select * from %s" % (MYSQL_TABLE_DATA)
        count = self._cursor.execute(sql)
        return count

    def getAll(self, sql, param=None):
        """
        @summary: 执行查询，并取出所有结果集
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list(字典对象)/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchall()
        else:
            result = False
        return result

    def getOne(self, sql, param=None):
        """
        @summary: 执行查询，并取出第一条
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchone()
        else:
            result = False
        return result

    def getMany(self, sql, num, param=None):
        """
        @summary: 执行查询，并取出num条结果
        @param sql:查询ＳＱＬ，如果有查询条件，请只指定条件列表，并将条件值使用参数[param]传递进来
        @param num:取得的结果条数
        @param param: 可选参数，条件列表值（元组/列表）
        @return: result list/boolean 查询到的结果集
        """
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        if count > 0:
            result = self._cursor.fetchmany(num)
        else:
            result = False
        return result

    def insertOne(self, sql, value):
        """
        @summary: 向数据表插入一条记录
        @param sql:要插入的ＳＱＬ格式
        @param value:要插入的记录数据tuple/list
        @return: insertId 受影响的行数
        """
        self._cursor.execute(sql, value)
        return self.__getInsertId()

    def insertMany(self, sql, values):
        """
        @summary: 向数据表插入多条记录
        @param sql:要插入的ＳＱＬ格式
        @param values:要插入的记录数据tuple(tuple)/list[list]
        @return: count 受影响的行数
        """
        count = self._cursor.executemany(sql, values)
        return count

    def __getInsertId(self):
        """
        获取当前连接最后一次插入操作生成的id,如果没有则为０
        """
        self._cursor.execute("SELECT @@IDENTITY AS id")
        result = self._cursor.fetchall()
        return result[0]['id']

    def __query(self, sql, param=None):
        if param is None:
            count = self._cursor.execute(sql)
        else:
            count = self._cursor.execute(sql, param)
        return count

    def update(self, sql, param=None):
        """
        @summary: 更新数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要更新的  值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def delete(self, sql, param=None):
        """
        @summary: 删除数据表记录
        @param sql: ＳＱＬ格式及条件，使用(%s,%s)
        @param param: 要删除的条件 值 tuple/list
        @return: count 受影响的行数
        """
        return self.__query(sql, param)

    def begin(self):
        """
        @summary: 开启事务
        """
        self._conn.autocommit(0)

    def end(self, option='commit'):
        """
        @summary: 结束事务
        """
        if option == 'commit':
            self._conn.commit()
        else:
            self._conn.rollback()

    def dispose(self, isEnd=1):
        """
        @summary: 释放连接池资源
        """
        if isEnd == 1:
            self.end('commit')
        else:
            self.end('rollback')
        self._cursor.close()
        self._conn.close()


if __name__ == '__main__':
    m = MysqlPool()
    # a = m.get_cookie()
    # m.restore(a)
    print(MYSQL_TABLE_DATA)
    menu_name = '热力'
    panret_id = '4001'
    isRep = '电力'

    b = m.select(menu_name, panret_id, isRep)
    print(b)

    m.dispose()
