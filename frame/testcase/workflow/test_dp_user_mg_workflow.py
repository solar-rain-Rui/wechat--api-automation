import pytest
import allure

from frame.common.logger import log


@allure.epic("企业微信接口自动化")
@allure.feature("业务流程测试(冒烟)")
@allure.story("部门-用户-消息业务流")
@allure.title("创建部门 → 创建用户 → 发送消息")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.smoke
@pytest.mark.workflow
class TestDepartmentUserMessageWorkflow:
    """
    部门-用户-消息业务流测试
    目的：验证企业微信核心业务流程的正确性
    流程：创建部门 → 创建用户 → 发送消息 → 验证结果
    """

    def test_department_user_message_workflow(
        self, 
        department_factory, 
        user_factory, 
        message_api
    ):
        """
        测试步骤：
        1. 创建部门
        2. 创建用户（属于该部门）
        3. 向用户发送消息
        4. 验证消息发送成功
        """

        log.info("========== 【部门-用户-消息业务流测试开始】 ==========")

        # Step 1: 创建部门
        log.info("Step 1: 创建测试部门")
        department_data = {
            "name": "${auto}",
            "parentid": "${auto}"
        }
        create_dept_res = department_factory.create(department_data)
        create_dept_json = create_dept_res.json()
        dept_info = department_factory.get_created(0)
        log.info(f"已创建部门: {dept_info}")
        assert create_dept_res.status_code == 200
        assert create_dept_json["errcode"] == 0, f"创建部门失败: {create_dept_json}"
        
        dept_id = create_dept_json.get("id")
        dept_name = create_dept_json.get("name")
        log.info(f" 部门创建成功，部门ID: {dept_id}, 部门名称: {dept_name}")

        # Step 2: 创建用户（属于该部门）
        log.info("Step 2: 创建测试用户")
        user_data = {
            "userid": "${auto}",
            "name": "${auto}",
            "mobile": "${auto}",
            "department": [dept_id]
        }
        create_user_res = user_factory(user_data)
        create_user_json = create_user_res.json()
        
        assert create_user_res.status_code == 200
        assert create_user_json["errcode"] == 0, f"创建用户失败: {create_user_json}"
        
        user_id = getattr(create_user_res, "created_userid")
        user_name = create_user_json.get("name")
        log.info(f" 用户创建成功，用户ID: {user_id}, 用户名称: {user_name}, 所属部门ID: {dept_id}")

        # Step 3: 向用户发送消息
        log.info("Step 3: 向用户发送文本消息")
        message_data = {
            "agentid": 1000002,
            "content": "自动化测试-业务流测试消息",
            "touser": user_id,
            "toparty": None,
            "totag": None,
            "safe": 0
        }
        send_message_res = message_api.send_message(message_data)
        send_message_json = send_message_res.json()
        
        log.info(f"消息发送响应: {send_message_json}")

        # Step 4: 验证消息发送成功
        log.info("Step 4: 验证消息发送结果")
        assert send_message_res.status_code == 200
        assert send_message_json["errcode"] == 0, f"消息发送失败: {send_message_json}"
        
        log.info(f" 消息发送成功，已发送给用户: {user_id}")
        log.info("========== 【部门-用户-消息业务流测试完成】 ==========")


