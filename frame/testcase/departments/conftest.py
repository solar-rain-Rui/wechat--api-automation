# 局部fixture，注入department_api
import pytest
from frame.apis.contacts.departments import Departments

@pytest.fixture(scope="class")
def department_api(token):
    """部门模块的 API 实例"""
    return Departments(token=token)
