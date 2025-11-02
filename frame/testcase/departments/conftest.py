# 局部fixture，注入department_api
import pytest
import time
import random
from frame.apis.contacts.departments import Departments
from frame.common.db import DBUtil



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




#结合本地数据库模拟，在执行用例前先执行对应sql语句，来验证数据库断言逻辑
@pytest.fixture(scope="function")
def fake_department(db):
    """
    每个用例运行前：插入一条模拟的部门数据
    用例运行后：自动删除这条数据
    """
    dept_id = 2001
    dept_name = "接口测试部A"

    # 1️⃣ 插入一条测试数据
    db.execute(
        "INSERT INTO departments (id, name, parentid) VALUES (%s, %s, %s)",
        (dept_id, dept_name, 1)
    )

    # 2️⃣ yield 表示这里执行完之后暂停，等测试用例执行完再往下走
    yield dept_id  # 把这个部门ID提供给测试用例用

    # 3️⃣ 清理数据
    db.execute("DELETE FROM departments WHERE id = %s", (dept_id,))

