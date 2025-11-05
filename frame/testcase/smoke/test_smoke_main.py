import pytest
import allure
from frame.apis.contacts.departments import Departments
from frame.apis.contacts.users import Users
from frame.apis.contacts.tags import Tags


@allure.feature("企业微信主链路冒烟测试")
class TestSmokeMain:
    @allure.story("部门→用户→标签 主链路验证")
    @pytest.mark.smoke
    def test_main_flow(self):
        dep_api = Departments()
        user_api = Users()
        tag_api = Tags()

        # Step 1️⃣ 创建部门
        with allure.step("创建部门"):
            dep_name = "冒烟测试部门"
            dep_res = dep_api.create({"name": dep_name, "parentid": 1}).json()
            print("【创建部门返回】=>", dep_res)  #  临时调试
            dep_id=dep_res["id"]
            assert dep_res["errcode"] == 0, f"创建部门失败：{dep_res}"

        # Step 2️⃣ 创建用户（并关联部门）
        with allure.step("创建用户"):
            userid = "smoke_user_001"
            name = "冒烟用户"
            data = {
                "userid": userid,
                "name": name,
                "department": [dep_id],
                "mobile": "13800000001"
            }
            res = user_api.create(data)
            res_json = res.json()
            assert res_json["errcode"] == 0, f"创建用户失败：{res_json}"

        # Step 3️⃣ 创建标签
        with allure.step("创建标签"):
            tag_name = "冒烟标签"
            tag_id = 999
            res = tag_api.create(tagname=tag_name, tagid=tag_id)
            res_json = res.json()
            assert res_json["errcode"] == 0, f"创建用户失败：{res_json}"

        # Step 4️⃣ 将用户加入标签
        with allure.step("给用户打标签"):
            res = tag_api.add_users(tagid=tag_id, userlist=[userid])
            res_json = res.json()
            assert res_json["errcode"] == 0, f"创建用户失败：{res_json}"

        # Step 5️⃣ 查询标签成员
        with allure.step("查询标签成员"):
            res = tag_api.get_users(tagid=tag_id)
            res_json = res.json()
            assert res_json["errcode"] == 0, f"创建用户失败：{res_json}"
            assert any(u["userid"] == userid for u in res_json["userlist"]), "标签成员校验失败"

        allure.dynamic.title("部门→用户→标签 主链路冒烟测试通过 ✅")
