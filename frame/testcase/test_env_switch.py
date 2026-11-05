from frame.common.config import cf


def test_env_switch():
    base_url = cf.get("base_url")
    print(f"当前加载的环境配置文件：{cf.loaded_file}")
    print(f"当前加载的 base_url 是：{base_url}")
    # 不打印 cf.data 全量内容，避免密钥等敏感配置输出到终端与 CI 日志
    assert base_url is not None
