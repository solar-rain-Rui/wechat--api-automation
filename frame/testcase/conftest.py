
import random
from types import SimpleNamespace

import pytest
import copy
import uuid

from frame.apis.contacts.departments import Departments
from frame.apis.contacts.tags import Tags
from frame.apis.contacts.users import Users
from frame.apis.message.message import MessageApi
from frame.common.token_get import fetch_token
from frame.common.utils.tools import load_yaml
from frame.common.logger import log


# #准备测试数据
# @pytest.fixture(scope="session", autouse=True)
# def prepare_env_data(token):
#     """在整个测试会话开始前准备数据"""
#     log.info("开始执行环境数据准备...")
#     # 复用已经获取好的 token，避免数据准备阶段出现 access_token 缺失
#     prepare_all_test_data(departments=True, users=True, tags=True, token=token)
#     log.info("环境数据准备完成。")



@pytest.fixture(scope="session")
def token():
    """获取全局 token，只执行一次"""
    print(" token fixture 被执行了")

    return fetch_token()


#统一管理业务接口对象的fixture
@pytest.fixture(scope="session")
def department_api(token): #获取的token传进来
    """部门模块的 API 实例"""
    print(" department_api fixture 被执行")
    return Departments(token=token)

@pytest.fixture(scope="session")
def user_api(token):
    """提供用户模块接口实例"""
    return Users(token=token)

@pytest.fixture(scope="session")
def tag_api(token):
    """提供标签接口实例"""
    return Tags(token=token)

@pytest.fixture(scope="session")
def message_api(token):
    """消息模块的 API 实例"""
    return MessageApi(token=token)

def replace_auto_placeholder(data, root_dept_id=1):
    """
    统一的数据预处理函数：替换数据中的 ${auto} 占位符
    支持 pytest-xdist 并发安全，使用 uuid 保证唯一性
    
    处理规则：
    - name: "${auto}" -> 生成唯一部门名称（使用 uuid）
    - parentid: "${auto}" -> 使用根部门ID（默认1）
    - id: "${auto}" -> 移除该字段（由API自动生成）
    - 其他字段: "${auto}" -> 根据字段类型生成唯一值
    
    参数:
        data: 待处理的数据字典
        root_dept_id: 根部门ID，默认为1
    
    返回:
        处理后的数据字典（深拷贝）
    """
    if not isinstance(data, dict):
        return data
    
    result = copy.deepcopy(data)
    # 使用 uuid4 生成唯一标识，保证并发安全
    unique_id = uuid.uuid4().hex[:8]  # 取前8位，足够唯一且可读
    
    # 收集需要删除的键（id字段），避免在遍历时修改字典
    keys_to_remove = []
    
    for key, value in result.items():
        if value == "${auto}":
            if key == "name":
                result[key] = f"test_部门_{unique_id}"
            elif key == "parentid":
                result[key] = root_dept_id
            elif key == "id":
                # id 字段如果是 ${auto}，标记为删除（由API自动生成）
                keys_to_remove.append(key)
            else:
                # 其他字段的 ${auto} 处理，可根据需要扩展
                # 默认使用唯一字符串
                result[key] = f"auto_{unique_id}"
        elif isinstance(value, dict):
            result[key] = replace_auto_placeholder(value, root_dept_id)
        elif isinstance(value, list):
            result[key] = [
                replace_auto_placeholder(item, root_dept_id) if isinstance(item, dict) else item 
                for item in value
            ]
    
    # 删除标记的键
    for key in keys_to_remove:
        result.pop(key, None)
    
    return result


def replace_auto_placeholder_user(data, root_dept_id=1):
    """
    用户模块：替换 data 中的 ${auto} 占位符
    - userid -> test_user_{uuid}
    - name -> test_用户_{uuid}
    - mobile -> 138 开头的 11 位数字
    - email -> test_{uuid}@test.com
    - position -> test_pos_{uuid}
    - department 列表中 "${auto}" -> root_dept_id
    """
    if not isinstance(data, dict):
        return data
    result = copy.deepcopy(data)
    unique_id = uuid.uuid4().hex[:8]
    mobile_suffix = str(random.randint(100000000, 999999999))  # 8 位，加上 138 共 11 位
    for key, value in result.items():
        if value == "${auto}":
            if key == "userid":
                result[key] = f"test_user_{unique_id}"
            elif key == "name":
                result[key] = f"test_用户_{unique_id}"
            elif key == "mobile":
                result[key] = f"138{mobile_suffix}"
            elif key == "email":
                result[key] = f"test_{unique_id}@test.com"
            elif key == "position":
                result[key] = f"test_pos_{unique_id}"
            else:
                result[key] = f"auto_{unique_id}"
        elif key == "department" and isinstance(value, list):
            result[key] = [
                root_dept_id if item == "${auto}" else item
                for item in value
            ]
        elif isinstance(value, dict):
            result[key] = replace_auto_placeholder_user(value, root_dept_id)
    return result


def replace_auto_placeholder_tag(data):
    """
    标签模块：替换 data 中的 ${auto} 占位符
    - tagname -> test_标签_{uuid}
    - tagid 为 "${auto}" 时从 data 中移除，由 API 自动生成
    """
    if not isinstance(data, dict):
        return data
    result = copy.deepcopy(data)
    unique_id = uuid.uuid4().hex[:8]
    keys_to_remove = []
    for key, value in result.items():
        if value == "${auto}":
            if key == "tagname":
                result[key] = f"test_标签_{unique_id}"
            elif key == "tagid":
                keys_to_remove.append(key)
            else:
                result[key] = f"auto_{unique_id}"
        elif isinstance(value, dict):
            result[key] = replace_auto_placeholder_tag(value)
    for k in keys_to_remove:
        result.pop(k, None)
    return result


@pytest.fixture
def department_factory(department_api):
    """
    资源生命周期管理：
    - 自动处理 ${auto} 占位符
    - 自动记录创建的部门
    - 测试结束自动清理
    """
    created_ids = []
    created_depts = []  # 存储创建的部门信息，用于后续查询

    def _create(data):
        """创建部门，自动处理 ${auto} 占位符"""
        # 使用统一的预处理函数替换 ${auto} 占位符
        processed_data = replace_auto_placeholder(data)
        
        res = department_api.create(processed_data)
        res_json = res.json()
        dep_id = res_json.get("id")
        
        if dep_id:
            created_ids.append(dep_id)
            created_depts.append({
                "id": dep_id,
                "name": processed_data.get("name"),
                "data": processed_data
            })
        
        return res
    
    def _get_created_dept(index=0):
        """获取已创建的部门信息"""
        if index < len(created_depts):
            return created_depts[index]
        return None

    # 返回创建函数和查询函数
    factory = SimpleNamespace(
        create=_create,
        get_created=_get_created_dept,
        created_ids=created_ids,
    )
    
    yield factory

    # ===== 测试结束自动清理(批量清理) =====
    if created_ids:
        log.info("[factory] 开始批量清理部门")
    for dep_id in created_ids:
        try:
            department_api.delete(dep_id)
            log.info(f"🧹 自动清理测试部门：{dep_id}")
        except Exception as e:
            log.warning(f"清理部门 {dep_id} 失败: {e}")


@pytest.fixture
def user_factory(user_api):
    """
    用户资源 factory fixture：
    - 返回可调用的 _create，按需创建用户
    - 自动记录创建的 userid，teardown 时统一清理
    """
    created_ids = []

    def _create(data):
        processed = replace_auto_placeholder_user(data)
        res = user_api.create(processed)
        res_json = res.json()
        if res_json.get("errcode") == 0 and processed.get("userid"):
            created_ids.append(processed["userid"])
        # 供 get/update/delete 用例获取本次创建的 userid
        setattr(res, "created_userid", processed.get("userid"))
        return res

    yield _create

    if created_ids:
        log.info("[factory] 开始批量清理用户")
    for userid in created_ids:
        try:
            user_api.delete(userid)
            log.info(f" 自动清理测试用户：{userid}")
        except Exception as e:
            log.warning(f"清理用户 {userid} 失败: {e}")


@pytest.fixture
def tag_factory(tag_api):
    """
    标签资源 factory fixture：
    - 返回可调用的 _create，按需创建标签
    - 自动记录创建的 tagid，teardown 时统一清理
    """
    created_ids = []

    def _create(data):
        processed = replace_auto_placeholder_tag(data)
        tagname = processed["tagname"]
        tagid = processed.get("tagid")
        if tagid == "${auto}" or tagid is None:
            tagid = None
        res = tag_api.create(tagname=tagname, tagid=tagid)
        res_json = res.json()
        if res_json.get("errcode") == 0:
            tid = res_json.get("tagid")
            if tid is not None:
                created_ids.append(tid)
        # 供 get/update/delete 用例获取本次创建的 tagid
        setattr(res, "created_tagid", res_json.get("tagid"))
        return res

    yield _create

    if created_ids:
        log.info("[factory] 开始批量清理标签")
    for tagid in created_ids:
        try:
            tag_api.delete(tagid)
            log.info(f" 自动清理测试标签：{tagid}")
        except Exception as e:
            log.warning(f"清理标签 {tagid} 失败: {e}")








# @pytest.fixture(scope="session", autouse=True)
# def clean_created_data(token):
#
#     print(">>> CLEAN FIXTURE LOADED")
#
#     yield  # 等全部用例执行完
#     print(">>> CLEAN EXECUTED")
#
#     log.info("🧹 开始清理创建用例产生的数据...")
#
#     # 1. 清理部门（名称以 test_ 开头）
#     dept_api = Departments(token=token)
#     for dep_id in CREATED_DEPT_IDS:
#         try:
#             dept_api.delete(dep_id)
#             log.info(f"🗑 删除测试部门：{dep_id}")
#         except Exception as e:
#             log.warning(f"删除部门 {dep_id} 失败: {e}")
#     # deps = dept_api.list_all().json()
#     # print("【所有部门信息】=>", deps)
#     #
#     # dept_list = dept_api.list_all().json().get("department", [])
#     # for d in dept_list:
#     #     if d["name"].startswith("test_")or "test_" in d["name"]:
#     #         dept_api.delete(d["id"])
#     #         log.info(f"🗑 删除测试部门：{d['name']}")
#
#     # 2. 清理用户（userid 以 test_ 开头）
#     user_api = Users(token=token)
#
#     for userid in CREATED_USER_IDS:
#         try:
#             res = user_api.delete(userid)
#             log.info(f"🗑 删除测试用户：{userid}, 返回：{res.json()}")
#         except Exception as e:
#             log.warning(f"❌ 删除用户 {userid} 失败: {e}")
#
#     # 3. 清理标签（tagname 以 test_ 开头）
#     tag_api = Tags(token=token)
#     tag_list = tag_api.list().json().get("taglist", [])
#     for t in tag_list:
#         if t["tagname"].startswith("test_"):
#             tag_api.delete(t["tagid"])
#             log.info(f"🗑 删除测试标签：{t['tagname']}")
