import pytest
from frame.common.config import Config
#管理多环境的pytest配置文件
#  添加命令行参数 --env
def pytest_addoption(parser):
    parser.addoption(
        "--env",                  # 参数名
        action="store",           # 保存参数值
        default="test_env",       # 默认环境（你的项目默认就是 test_env.yaml）
        help="运行环境: test_env / dev / prod"
    )

# 全局 fixture，自动在整个会话加载
@pytest.fixture(scope="session", autouse=True)
def global_config(pytestconfig):
    env = pytestconfig.getoption("env")  # 获取命令行传入的 --env 值
    #重新实例化配置
    #from common import config
    Config.cf = Config(f"{env}.yaml")  # 动态加载对应环境文件
