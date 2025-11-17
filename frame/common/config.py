import os
import yaml
#集中管理环境参数
class Config:
    def __init__(self, env=None):
        base = os.path.dirname(os.path.dirname(__file__))  # frame/

        if env:
            filename=f"config/{env}"
        else:
            filename="config/test_env.yaml"

        path = os.path.join(base, filename)
        with open(path, encoding="utf-8") as f:
            self.data = yaml.safe_load(f)
        print(f" 当前加载的环境配置文件: {filename}")
    def get(self, key, default=None):
        return self.data.get(key, default)

# 方便导入 cf
cf = Config()
