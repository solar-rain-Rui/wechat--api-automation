# 局部fixture，注入department_api
import time

import pytest

from frame.apis.contacts.departments import Departments
from frame.common.db import DBUtil
from frame.common.logger import log


# 每次测试用例都会自动创建一个临时部门；
# 测试结束后，自动删除。
@pytest.fixture(scope="function")
def temp_department(department_api,request):
    """按需创建临时部门：每个测试用例运行前创建，结束后自动删除"""
    # 如果测试用例中有参数（通过 param 传入）
    param = getattr(request, "param", None) or {}
    dep_data = {
        "name": param.get("name", f"按需测试部门_{int(time.time()) % 10000}"),  # 必须有合法 name
        "parentid": param.get("parentid", 1)
    }

    # 创建部门
    create_res = department_api.create(dep_data)
    res_json = create_res.json()
    errcode = res_json.get("errcode")

    if errcode != 0:
        raise Exception(f"❌ 创建部门失败：{res_json}")

    dep_id = res_json.get("id")
    log.info(f"按需创建测试部门成功，id={dep_id}，响应={res_json}")
    # 返回部门 id 给测试用例使用
    yield dep_id

    # 测试结束自动清理
    if dep_id:
        department_api.delete({"id": dep_id})
        log.info(f"按需删除测试部门 id={dep_id}")
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

