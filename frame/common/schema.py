import json
from jsonschema import validate, ValidationError
from frame.common.logger import Logger
import os

log=Logger().get_logger()

class SchemaValidator:
    @staticmethod
    def validate_json(data: dict, schema_path: str):
        """
        校验接口返回数据是否符合 JSON Schema
        :param data: 实际接口返回的 JSON 数据（dict）
        :param schema_path: schema 文件路径
        """
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"未找到 schema 文件：{schema_path}")

        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        try:
            validate(instance=data, schema=schema)
            log.info("✅ JSON Schema 校验通过")
            return True
        except ValidationError as e:
            log.error(f"❌ JSON Schema 校验失败: {e.message}")
            log.error(f"出错路径: {' → '.join([str(x) for x in e.path])}")
            raise AssertionError(f"JSON Schema 校验失败: {e.message}")
