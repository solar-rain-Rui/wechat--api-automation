import pytest

from frame.common.config import cf


# 管理多环境的pytest配置文件
# 添加命令行参数 --env
def pytest_addoption(parser):
    parser.addoption(
        "--env",                  # 参数名
        action="store",           # 保存参数值
        default="test_env",       # 默认环境（项目默认就是 test_env.yaml）
        help="运行环境: test_env / dev / prod"
    )


# 全局 fixture，自动在整个会话加载
@pytest.fixture(scope="session", autouse=True)
def global_config(pytestconfig):
    """
    根据命令行 --env 参数重新加载环境配置。
    通过 cf.reload() 原地替换 data，保证所有持有 cf 引用的模块
    （BaseApi、token_get 等）读到的都是切换后的配置。
    """
    env = pytestconfig.getoption("env")
    cf.reload(env)
