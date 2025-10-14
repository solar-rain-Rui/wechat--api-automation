
import yaml
class Utils:

    @classmethod
    def get_yaml_data(cls,file_path):
        """
        读取yaml文件
        :param file_path: yaml文件的路径
        :return: yaml文件的内容
        """
        with open(file_path, "r", encoding="utf-8") as f:
            datas=yaml.safe_load(f)
        return datas