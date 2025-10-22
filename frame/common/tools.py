import os
import yaml

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
