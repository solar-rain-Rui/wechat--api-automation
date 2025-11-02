# frame/testcases/conftest.py
import pytest

from frame.apis.contacts.departments import Departments
from frame.common.db import DBUtil
from frame.common.tools import load_yaml
from frame.common.logger import log
from frame.apis.wework import WeWork  # 全局入口

@pytest.fixture(scope="session")
def cfg():
    """全局配置对象"""
    return load_yaml("config/test_env.yaml")

@pytest.fixture(scope="session")
def token():
    """获取全局 token，只执行一次"""
    wk = WeWork()
    return wk.token

@pytest.fixture(scope="session")
def db():
    """提供数据库连接实例"""
    db = DBUtil(
        host="localhost",
        user="root",
        password="root1997",
        database="wecom_test"
    )
    yield db
    db.close()

@pytest.fixture(scope="session")
def department_api(token):
    """部门模块的 API 实例"""
    return Departments(token=token)