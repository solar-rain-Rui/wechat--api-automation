import os
import yaml


# 集中管理环境参数
class Config:
    def __init__(self, env=None):
        # frame/ 目录，配置文件统一放在 frame/config/ 下
        self.base = os.path.dirname(os.path.dirname(__file__))
        self.data = {}
        self.loaded_file = None
        self.reload(env)

    def reload(self, env=None):
        """
        重新加载指定环境的配置文件，并原地进行数据替换。
        所有通过 cf.get() 读取配置的代码立即生效，
        解决了重新赋值新实例后旧引用读不到新配置的问题。
        :param env: 形如 "test_env" / "dev" / "prod"（可带可不带 .yaml 后缀）
        """
        if env:
            filename = f"config/{env}" if env.endswith(".yaml") else f"config/{env}.yaml"
        else:
            filename = "config/test_env.yaml"

        path = os.path.join(self.base, filename)
        with open(path, encoding="utf-8") as f:
            self.data = yaml.safe_load(f)
        self.loaded_file = filename
        self._apply_sensitive_overrides()
        print(f"当前加载的环境配置文件: {filename}")

    def _apply_sensitive_overrides(self):
        """
        敏感配置项支持从环境变量读取，避免真实密钥写入仓库。
        支持两种来源（优先级从高到低）：
        1. 操作系统环境变量 WECOM_CORPID / WECOM_CORPSECRET
        2. 项目根目录 .env 文件（KEY=VALUE，已被 Git 忽略）
        """
        self._load_dotenv()

        corpid = os.getenv("WECOM_CORPID")
        if corpid and isinstance(self.data.get("corpid"), dict):
            self.data["corpid"]["接口自动化测试"] = corpid

        corpsecret = os.getenv("WECOM_CORPSECRET")
        if corpsecret and isinstance(self.data.get("corpsecret"), dict):
            self.data["corpsecret"]["contacts"] = corpsecret

    @staticmethod
    def _load_dotenv(path=None):
        """极简 .env 加载器（仅支持 KEY=VALUE 与 # 注释），不引入第三方依赖"""
        if path is None:
            # 项目根目录：frame/common/config.py 向上三层
            path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"
            )
        if not os.path.exists(path):
            return
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                # setdefault：操作系统真实环境变量优先于 .env 文件
                os.environ.setdefault(key.strip(), value.strip())

    def get(self, key, default=None):
        return self.data.get(key, default)


# 方便导入 cf（全局唯一实例，环境切换通过 cf.reload() 原地更新）
cf = Config()
