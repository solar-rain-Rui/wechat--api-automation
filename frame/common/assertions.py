
from jsonpath import jsonpath
from frame.common.logger import Logger
log=Logger().get_logger()
class AssertUtil:
    """
    jsonpath断言工具类
    用来断言接口响应中的字段值
    """
    @staticmethod
    def assert_json_value(resp_json, json_path, expect_value):
        """
       断言响应体中指定 JSONPath 路径的值是否等于期望值

       :param resp_json: 接口响应（dict）
       :param json_path: JSONPath 表达式（例如 "$.errcode" 或 "$.department[0].name"）
       :param expect_value: 期望值
        """
        #提取jsonpath对应的实际值
        actual = jsonpath(resp_json, json_path)
        if not actual:
            #如果路径错误或字段不存在，记录错误日志并抛异常
            log.error(f"未找到 JSONPath 路径: {json_path}")
            raise AssertionError(f"未找到 JSONPath 路径: {json_path}")

            # 比较结果
        actual_value = actual[0]
        if actual_value == expect_value:
            log.info(f"✅ JSONPath 断言成功：{json_path} = {expect_value}")
        else:
            log.error(
                f"\n❌ JSONPath 断言失败：{json_path}\n"
                f"期望值: {expect_value}\n"
                f"实际值: {actual_value}\n"
            )
            raise AssertionError(
                f"JSONPath 断言失败: {json_path} → 期望值: {expect_value}, 实际值: {actual_value}"
            )



