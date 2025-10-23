# frame/testcases/conftest.py
import pytest
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
