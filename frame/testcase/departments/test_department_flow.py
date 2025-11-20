import pytest
import allure
from frame.common.logger import log

@allure.epic("企业微信接口自动化")
@allure.feature("部门管理")
@allure.story("部门业务流：创建 → 修改 → 查询 → 删除")
@allure.severity(allure.severity_level.CRITICAL)
class TestDepartmentsFlow:
    """
    部门模块 - 业务流测试
    目的：验证部门的增、改、查、删接口能否顺利联动运行，形成完整业务闭环。
    """

    @pytest.mark.flow
    def test_department_business_flow(self, department_api):
        """
        测试流程：
        1️⃣ 创建部门
        2️⃣ 修改部门
        3️⃣ 获取部门详情
        4️⃣ 删除部门
        """

        log.info("========== 【部门业务流测试开始】 ==========")

        # 1️⃣ 创建部门
        log.info("Step 1: 创建部门")
        create_name = "业务流测试部门"
        create_res = department_api.create({ "name": create_name,
                                         "parentid": 1})  # parentid=1
        log.info(f"创建部门响应: {create_res.json()}")
        assert create_res.json()["errcode"] == 0
        dep_id = create_res.json()["id"]

        # 2️⃣ 修改部门
        log.info("Step 2: 修改部门名称")
        updata_name="修改后的业务流部门"
        update_data = {
            "id": dep_id,
            "name": updata_name
        }
        update_res = department_api.update(update_data)
        log.info(f"修改部门响应: {update_res.json()}")
        assert update_res.json()["errcode"] == 0

        # 3️⃣ 获取部门详情
        log.info("Step 3: 获取部门详情")
        get_res = department_api.get(dep_id)
        log.info(f"查询部门响应: {get_res.json()}")
        # 先检查接口是否成功
        assert get_res.json()["errcode"] == 0, f"查询部门失败: {get_res.json()}"
        # department_id 列表
        departments = get_res.json().get("department_id")
        assert departments, f"部门列表为空: {get_res.json()}"
        # 断言某个部门 ID 存在
        #  update_name 对应的部门是 dep_id
        found = any(d["id"] == dep_id for d in departments)
        assert found, f"部门ID {dep_id} 未找到"


        # 4️⃣ 删除部门
        log.info("Step 4: 删除部门")
        delete_res = department_api.delete(dep_id)
        log.info(f"删除部门响应: {delete_res.json()}")
        assert delete_res.json()["errcode"] == 0

        log.info("========== 【部门业务流测试结束】 ==========")
