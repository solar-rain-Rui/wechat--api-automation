# 局部fixture，注入department_api
import pytest
import time
import random
from frame.apis.contacts.departments import Departments



@pytest.fixture(scope="session")
def department_api(token):
    """部门模块的 API 实例"""
    return Departments(token=token)
# 每次测试用例都会自动创建一个临时部门；
# 测试结束后，自动删除。
@pytest.fixture(scope="function")
def temp_department(department_api):
    """创建临时部门，测试结束后清理"""
    # 用时间戳生成唯一部门名
    dept_name = f"自动化测试_{int(time.time())}_{random.randint(1000,9999)}"
    data = {"name": dept_name, "parentid": 1}
    res = department_api.create(data)
    assert res.json().get("errcode") == 0, f"创建部门失败: {res.json()}"
    dept_id = res.json().get("id")
    yield dept_id

    # 删除前检查
    if dept_id:
        department_api.delete({"id": dept_id})
        print("清除临时部门")
