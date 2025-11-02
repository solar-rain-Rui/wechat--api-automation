import uuid
import random

import pytest
import time
from frame.apis.contacts.users import Users

@pytest.fixture(scope="session")
def user_api(token):
    """提供用户模块接口实例"""
    return Users(token=token)



@pytest.fixture(scope="function")
def temp_department(department_api):
    """创建临时部门，用于用户管理测试"""
    data = {
        "name": "temp_user_dep",
        "name_en": "temp_user_dep_en"
    }
    res = department_api.create(data)
    print(">>> 创建部门返回：", res.json())  # 👈 看这行输出
    depart_id = res.json().get("id")
    yield depart_id
    department_api.delete(depart_id)

@pytest.fixture(scope="function")
def temp_user(user_api, temp_department):
    """临时创建成员，测试结束后清理"""
    user_data = {
        "userid": f"auto_user_{uuid.uuid4().hex[:6]}",
        "name": "临时测试成员",
        "mobile": f"138{random.randint(10000000,99999999)}",
        "department": [temp_department],
    }
    res = user_api.create(user_data)
    res_json = res.json()
    assert res_json["errcode"] == 0

    yield user_data["userid"]

    # 清理成员
    user_api.delete(user_data["userid"])
