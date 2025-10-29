# frame/common/db_handler.py
import pymysql
from frame.common.logger import log

class DBUtil:
    def __init__(self, host, user, password, database, port=3306):
        self.conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.conn.cursor()
        log.info("✅ DB connected")

    def query(self, sql, params=None):
        """执行查询，返回所有结果（列表 of dict）"""
        log.info(f"执行查询: {sql} | params: {params}")
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def fetch_one(self, sql, params=None):
        """执行查询，返回单条记录（dict 或 None）"""
        log.info(f"执行查询(fetch_one): {sql} | params: {params}")
        self.cursor.execute(sql, params)
        return self.cursor.fetchone()

    def execute(self, sql, params=None):
        """
        执行 INSERT/UPDATE/DELETE（支持参数化）
        params 可以是 tuple 或 list，或 None。
        """
        try:
            log.info(f"执行SQL: {sql} | params: {params}")
            self.cursor.execute(sql, params)
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            log.error(f"SQL执行失败: {e}")
            raise

    def close(self):
        try:
            self.cursor.close()
            self.conn.close()
            log.info("DB closed")
        except Exception:
            pass
