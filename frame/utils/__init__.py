# frame/utils/__init__.py
from frame.common import tools, logger, config

class Utils:
    get_yaml_data = staticmethod(lambda rel: tools.load_yaml(rel))
    get_logger = staticmethod(lambda name="auto_test": logger.get_logger(name))
    get_config = staticmethod(lambda key, default=None: config.cf.get(key, default))

# 旧代码可以继续使用：
# from frame.utils import Utils
# Utils.get_yaml_data("datas/departments.yaml")
