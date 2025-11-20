# frame/testcases/conftest.py
import pytest

from frame.apis.contacts.departments import Departments
from frame.apis.contacts.tags import Tags
from frame.apis.contacts.users import Users
from frame.common.db import DBUtil
from frame.common.tools import load_yaml, CREATED_DEPT_IDS, CREATED_USER_IDS
from frame.common.logger import log
from frame.apis.wework import WeWork  # 全局入口

from frame.setup.prepare_test_data import prepare_all_test_data




#准备测试数据
@pytest.fixture(scope="session", autouse=True)
def prepare_env_data():
    """在整个测试会话开始前准备数据"""
    log.info("开始执行环境数据准备...")
    prepare_all_test_data(departments=True, users=True, tags=True)
    log.info("环境数据准备完成。")


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


@pytest.fixture(scope="session", autouse=True)
def clean_created_data():

    print(">>> CLEAN FIXTURE LOADED")

    yield  # 等全部用例执行完
    print(">>> CLEAN EXECUTED")

    log.info("🧹 开始清理创建用例产生的数据...")

    # 1. 清理部门（名称以 test_ 开头）
    dept_api = Departments()
    for dep_id in CREATED_DEPT_IDS:
        try:
            dept_api.delete(dep_id)
            log.info(f"🗑 删除测试部门：{dep_id}")
        except Exception as e:
            log.warning(f"删除部门 {dep_id} 失败: {e}")
    # deps = dept_api.list_all().json()
    # print("【所有部门信息】=>", deps)
    #
    # dept_list = dept_api.list_all().json().get("department", [])
    # for d in dept_list:
    #     if d["name"].startswith("test_")or "test_" in d["name"]:
    #         dept_api.delete(d["id"])
    #         log.info(f"🗑 删除测试部门：{d['name']}")

    # 2. 清理用户（userid 以 test_ 开头）
    user_api = Users()

    for userid in CREATED_USER_IDS:
        try:
            res = user_api.delete(userid)
            log.info(f"🗑 删除测试用户：{userid}, 返回：{res.json()}")
        except Exception as e:
            log.warning(f"❌ 删除用户 {userid} 失败: {e}")

    # 3. 清理标签（tagname 以 test_ 开头）
    tag_api = Tags()
    tag_list = tag_api.list().json().get("taglist", [])
    for t in tag_list:
        if t["tagname"].startswith("test_"):
            tag_api.delete(t["tagid"])
            log.info(f"🗑 删除测试标签：{t['tagname']}")
