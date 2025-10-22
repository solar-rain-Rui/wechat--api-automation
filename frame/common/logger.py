import logging
import os
from datetime import datetime


class Logger:
    def __init__(self):
        # 1️⃣ 获取项目根目录
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # 2️⃣ 定义日志目录路径
        log_dir = os.path.join(base_path, "logs")
        os.makedirs(log_dir, exist_ok=True)

        # 3️⃣ 自动生成当天日志文件名
        log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")

        # 4️⃣ 创建 logger 对象(日志记录器)
        self.logger = logging.getLogger("AutoTestLogger")
        self.logger.setLevel(logging.INFO)

        # 避免重复添加 Handler
        if not self.logger.handlers:
            # 文件输出
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            console_handler = logging.StreamHandler()

            # 日志格式
            fmt = logging.Formatter(
                "%(asctime)s - [%(levelname)s] - %(filename)s:%(lineno)d - %(message)s"
            )
            file_handler.setFormatter(fmt)
            console_handler.setFormatter(fmt)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger


# 供全局直接导入使用
log = Logger().get_logger()
