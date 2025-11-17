import os
import yaml

# 全局列表，用来记录测试创建的部门 ID
CREATED_DEPT_IDS = []
# 记录用户ID
CREATED_USER_IDS = []

def get_frame_root():
    # 返回 frame 目录的绝对路径
    return os.path.dirname(os.path.dirname(__file__))

def load_yaml(relpath):
    """
    relpath 相对于 frame 的路径，例如: 'datas/departments.yaml'
    """
    base = get_frame_root()
    path = os.path.join(base, relpath)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)
