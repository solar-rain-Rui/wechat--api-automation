import os
import yaml
#集中管理环境参数
class Config:
    def __init__(self, env=None):
        base = os.path.dirname(os.path.dirname(__file__))  # frame/
        #取到frame路径
        if env:         #如果构造时传了 env，就用 config/<env>，否则默认读 config/test_env.yaml
            filename=f"config/{env}"
        else:
            filename="config/test_env.yaml"

        path = os.path.join(base, filename) #拼接出完整路径
        with open(path, encoding="utf-8") as f:
            self.data = yaml.safe_load(f) #将yaml解析加载到data
        print(f" 当前加载的环境配置文件: {filename}")
    def get(self, key, default=None): #提供访问
        return self.data.get(key, default)

# 方便导入 cf
cf = Config() #被导入时会实例化cf
