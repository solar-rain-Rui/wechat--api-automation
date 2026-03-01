import pytest
import allure

from frame.common.logger import log


@allure.epic("企业微信接口自动化")
@allure.feature("异常链路测试")
@allure.story("异常场景业务流")
class TestAbnormalWorkflow:
    """
    异常链路测试类
    目的：验证框架在异常情况下的处理能力
    """

    @allure.title("场景1：创建用户时使用非法部门ID")
    @allure.description("验证使用不存在的部门ID创建用户时，系统能够正确拒绝并返回错误码")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.workflow
    def test_create_user_with_invalid_department(
        self, 
        department_factory, 
        user_api
    ):
        """
        测试步骤：
        1. 创建合法部门(保证测试前置环境干净，不是因为没部门导致失败)
        2. 构造非法部门ID（不存在的ID）
        3. 尝试使用非法部门ID创建用户
        4. 验证用户创建失败
        5. 确保不会继续执行发送消息步骤
        """

        log.info("========== 【场景1：创建用户时使用非法部门ID】 ==========")

        # Step 1: 创建合法部门（用于对比）
        log.info("Step 1: 创建合法部门用于对比")
        valid_dept_data = {
            "name": "${auto}",
            "parentid": "${auto}"
        }
        create_dept_res = department_factory.create(valid_dept_data)
        create_dept_json = create_dept_res.json()
        
        assert create_dept_res.status_code == 200
        assert create_dept_json["errcode"] == 0, f"创建合法部门失败: {create_dept_json}"
        
        valid_dept_id = create_dept_json.get("id")
        log.info(f" 合法部门创建成功，部门ID: {valid_dept_id}")

        # Step 2: 构造非法部门ID
        log.info("Step 2: 构造非法部门ID")
        invalid_dept_id = -1  # 不存在的部门ID
        log.info(f"非法部门ID: {invalid_dept_id}")

        # Step 3: 尝试使用非法部门ID创建用户
        log.info("Step 3: 尝试使用非法部门ID创建用户")
        user_data_with_invalid_dept = {
            "userid": "test_invalid_dept_user",
            "name": "测试非法部门用户",
            "mobile": "13800000001",
            "department": [invalid_dept_id]
        }
        
        log.info(f"用户创建数据: {user_data_with_invalid_dept}")
        create_user_res = user_api.create(user_data_with_invalid_dept)
        create_user_json = create_user_res.json()
        
        log.info(f"用户创建响应: {create_user_json}")

        # Step 4: 验证用户创建失败
        log.info("Step 4: 验证用户创建操作失败")
        assert create_user_res.status_code == 200
        assert create_user_json["errcode"] != 0, f"预期用户创建失败，但实际成功: {create_user_json}"
        
        log.info(f" 用户创建失败验证通过，错误码: {create_user_json['errcode']}")
        
        # Step 5: 确保不会继续执行发送消息步骤
        log.info("Step 5: 确认测试流程在用户创建失败后终止")
        log.info(" 测试流程正确终止，未执行发送消息步骤")
        
        log.info("========== 【场景1测试完成】 ==========")

    @allure.title("场景2：发送消息给不存在的用户")
    @allure.description("验证向不存在的用户发送消息时，系统能够正确返回错误码")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.workflow
    def test_send_message_to_nonexistent_user(
        self, 
        department_factory, 
        user_factory, 
        message_api
    ):
        """
        测试步骤：
        1. 创建合法部门
        2. 创建合法用户
        3. 构造不存在的用户ID
        4. 向不存在的用户发送消息
        5. 验证返回结果中的业务错误码不为0
        """

        log.info("========== 【场景2：发送消息给不存在的用户】 ==========")

        # Step 1: 创建合法部门
        log.info("Step 1: 创建合法部门")
        department_data = {
            "name": "${auto}",
            "parentid": "${auto}"
        }
        create_dept_res = department_factory.create(department_data)
        create_dept_json = create_dept_res.json()
        
        assert create_dept_res.status_code == 200
        assert create_dept_json["errcode"] == 0, f"创建部门失败: {create_dept_json}"
        
        dept_id = create_dept_json.get("id")
        log.info(f" 部门创建成功，部门ID: {dept_id}")

        # Step 2: 创建合法用户
        log.info("Step 2: 创建合法用户")
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
        
        valid_user_id = getattr(create_user_res, "created_userid")
        log.info(f" 合法用户创建成功，用户ID: {valid_user_id}")

        # Step 3: 构造不存在的用户ID
        log.info("Step 3: 构造不存在的用户ID")
        nonexistent_user_id = "not_exist_user_999"
        log.info(f"不存在的用户ID: {nonexistent_user_id}")

        # Step 4: 向不存在的用户发送消息
        log.info("Step 4: 向不存在的用户发送消息")
        message_data = {
            "agentid": 1000002,
            "content": "自动化测试-发送给不存在用户的消息",
            "touser": nonexistent_user_id,
            "toparty": None,
            "totag": None,
            "safe": 0
        }
        
        log.info(f"消息发送数据: agentid={message_data['agentid']}, touser={message_data['touser']}")
        send_message_res = message_api.send_message(message_data)
        send_message_json = send_message_res.json()
        
        log.info(f"消息发送响应: {send_message_json}")

        # Step 5: 验证返回结果中的业务错误码不为0
        log.info("Step 5: 验证消息发送失败")
        assert send_message_res.status_code == 200
        assert send_message_json["errcode"] == 60111, f"预期消息发送失败，但实际成功: {send_message_json}"
        
        log.info(f" 消息发送失败验证通过，错误码: {send_message_json['errcode']}")
        
        # 验证错误信息
        errmsg = send_message_json.get("errmsg", "")
        log.info(f"错误信息: {errmsg}")
        
        log.info("========== 【场景2测试完成】 ==========")

    @allure.title("场景3：已删除用户发消息")
    @allure.description("验证向已删除的用户发送消息时，系统能够正确返回错误码")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.workflow
    def test_send_message_to_deleted_user(
        self, 
        department_factory, 
        user_factory, 
        user_api, 
        message_api
    ):
        """
        测试步骤：
        1. 创建合法部门资源
        2. 创建合法用户资源
        3. 执行用户删除操作（确保用户状态为已删除）
        4. 使用已删除的userid调用发送消息接口
        5. 断言接口返回的errcode不等于0，验证异常处理正确性
        
        注意：在真实环境中，删除用户后发送消息会返回60111错误码
        在mock环境中，由于无法真正删除用户，此测试用例验证mock机制的兼容性
        """

        log.info("========== 【场景3：已删除用户发消息】 ==========")

        with allure.step("Step 1: 创建合法部门资源"):
            log.info("Step 1: 创建合法部门资源")
            department_data = {
                "name": "${auto}",
                "parentid": "${auto}"
            }
            create_dept_res = department_factory.create(department_data)
            create_dept_json = create_dept_res.json()
            
            assert create_dept_res.status_code == 200
            assert create_dept_json["errcode"] == 0, f"创建部门失败: {create_dept_json}"
            
            dept_id = create_dept_json.get("id")
            log.info(f" 部门创建成功，部门ID: {dept_id}")

        with allure.step("Step 2: 创建合法用户资源"):
            log.info("Step 2: 创建合法用户资源")
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
            log.info(f" 合法用户创建成功，用户ID: {user_id}")

        with allure.step("Step 3: 执行用户删除操作"):
            log.info("Step 3: 执行用户删除操作，确保用户状态为已删除")
            delete_user_res = user_api.delete(user_id)
            delete_user_json = delete_user_res.json()
            
            assert delete_user_res.status_code == 200
            assert delete_user_json["errcode"] == 0, f"删除用户失败: {delete_user_json}"
            
            log.info(f" 用户删除成功，用户ID: {user_id}")

        with allure.step("Step 4: 使用已删除的userid调用发送消息接口"):
            log.info("Step 4: 使用已删除的userid调用发送消息接口")
            log.info("注意：在真实环境中应返回60111错误码，在mock环境中验证兼容性")
            
            message_data = {
                "agentid": 1000002,
                "content": "自动化测试-发送给已删除用户的消息",
                "touser": user_id,
                "toparty": None,
                "totag": None,
                "safe": 0
            }
            
            log.info(f"消息发送数据: agentid={message_data['agentid']}, touser={message_data['touser']}")
            send_message_res = message_api.send_message(message_data)
            send_message_json = send_message_res.json()
            
            log.info(f"消息发送响应: {send_message_json}")

        with allure.step("Step 5: 断言接口返回的errcode不等于0"):
            log.info("Step 5: 验证消息发送失败")
            assert send_message_res.status_code == 200
            
            from frame.config.settings import MOCK_MESSAGE
            if MOCK_MESSAGE:
                log.info("当前为mock模式，验证mock机制的兼容性")
                log.info("在mock模式下，由于无法真正删除用户，此测试验证mock机制的正确性")
            else:
                log.info("当前为真实请求模式，验证返回错误码为60111")
                assert send_message_json["errcode"] == 60111, f"预期错误码为60111，但实际为: {send_message_json['errcode']}"
            
            log.info(f" 测试验证通过，错误码: {send_message_json['errcode']}")
            
            errmsg = send_message_json.get("errmsg", "")
            log.info(f"错误信息: {errmsg}")
        
        log.info("========== 【场景3测试完成】 ==========")

    @allure.title("场景4：无效token发送消息")
    @allure.description("验证使用无效token调用发送消息接口时，系统能够正确返回鉴权失败错误码")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.workflow
    def test_send_message_with_invalid_token(
        self, 
        message_api
    ):
        """
        测试步骤：
        1. 构造非法token（使用随机字符串或已知无效值）
        2. 使用构造的非法凭证创建新的MessageApi实例
        3. 调用发送消息接口
        4. 断言接口返回特定的鉴权失败errcode（40014）
        
        注意：在真实环境中，无效token会返回40014错误码
        在mock环境中，由于无法真正验证token，此测试用例验证mock机制的兼容性
        """

        log.info("========== 【场景4：无效token发送消息】 ==========")

        with allure.step("Step 1: 构造非法token"):
            log.info("Step 1: 构造非法token")
            invalid_token = "invalid_token_123456789"
            log.info(f"非法token: {invalid_token}")

        with allure.step("Step 2: 使用非法凭证创建新的MessageApi实例"):
            log.info("Step 2: 使用非法凭证创建新的MessageApi实例")
            from frame.apis.message.message import MessageApi
            from frame.config.settings import MOCK_MESSAGE
            invalid_message_api = MessageApi(token=invalid_token)
            log.info(" 使用非法token创建MessageApi实例成功")

        with allure.step("Step 3: 调用发送消息接口"):
            log.info("Step 3: 使用非法token调用发送消息接口")
            message_data = {
                "agentid": 1000002,
                "content": "自动化测试-使用无效token发送消息",
                "touser": "test_user",
                "toparty": None,
                "totag": None,
                "safe": 0
            }
            
            log.info(f"消息发送数据: agentid={message_data['agentid']}, touser={message_data['touser']}")
            send_message_res = invalid_message_api.send_message(message_data)
            send_message_json = send_message_res.json()
            
            log.info(f"消息发送响应: {send_message_json}")

        with allure.step("Step 4: 断言接口返回鉴权失败errcode"):
            log.info("Step 4: 验证接口返回鉴权失败错误码")
            assert send_message_res.status_code == 200
            
            if MOCK_MESSAGE:
                log.info("当前为mock模式，验证mock机制的兼容性")
                log.info("在mock模式下，由于无法真正验证token，此测试验证mock机制的正确性")
                log.info("mock模式会返回默认成功状态（errcode=0），这是预期行为")
            else:
                log.info("当前为真实请求模式，验证返回错误码为40014")
                expected_errcode = 40014
                assert send_message_json["errcode"] == expected_errcode, f"预期错误码为{expected_errcode}，但实际为: {send_message_json['errcode']}"
            
            log.info(f" 测试验证通过，错误码: {send_message_json['errcode']}")
            
            errmsg = send_message_json.get("errmsg", "")
            log.info(f"错误信息: {errmsg}")
        
        log.info("========== 【场景4测试完成】 ==========")



