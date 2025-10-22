import os
import yaml
#集中管理环境参数
class Config:
    def __init__(self, filename="config/test_env.yaml"):
        base = os.path.dirname(os.path.dirname(__file__))  # frame/
        path = os.path.join(base, filename)
        with open(path, encoding="utf-8") as f:
            self.data = yaml.safe_load(f)

    def get(self, key, default=None):
        return self.data.get(key, default)

# 方便导入 cf
cf = Config()
