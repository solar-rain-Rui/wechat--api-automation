from frame.common.config import cf

def test_env_switch():
    base_url = cf.get("base_url")
    print(f"当前加载的 base_url 是：{base_url}")
    print(f"当前环境配置内容：")
    print(cf.data)
    assert base_url is not None
