

import logging
import os

from frame.utils.utils import Utils

# 实例化logger对象
logger = logging.getLogger(__name__)

# 判断路径是否存在，不存在就创建
log_path = os.sep.join([Utils.get_frame_root_path(), "logs"])

if not os.path.exists(log_path):
    os.mkdir(log_path)

# 绑定log的handler
file_handler = logging.FileHandler(filename=f"{log_path}/api_object.log", encoding="utf-8")

# 输出的formatter
formatter = logging.Formatter(
    '[%(asctime).19s] %(process)d:%(levelname).1s %(filename)s:%(lineno)d:%(funcName)s: %(message)s]')

# 日志格式与句柄的绑定
file_handler.setFormatter(formatter)

# 控制台句柄定义
steam_handler = logging.StreamHandler()
# 日志格式与句柄的绑定
steam_handler.setFormatter(formatter)

# 与logger进行绑定
logger.addHandler(file_handler)
logger.addHandler(steam_handler)

# 设置展示/写入文件的日志的级别
logger.setLevel(logging.INFO)