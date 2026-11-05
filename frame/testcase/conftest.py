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
from frame.common.logger import log


@pytest.fixture(scope="session")
def token():
    """获取全局 token，只执行一次"""
    return fetch_token()


# 统一管理业务接口对象的fixture
@pytest.fixture(scope="session")
def department_api(token):
    """部门模块的 API 实例"""
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


# ============================================================
# ${auto} 占位符处理
#
# 设计说明：
# _process_auto 是三个业务函数公共的处理引擎，负责
# 「深拷贝 + 递归遍历 + 按规则替换」这一完全相同的骨架；
# 各业务函数只保留自己的替换规则表（字段名 -> 生成规则），
# 业务差异不再混在遍历逻辑里。
# ============================================================

# 特殊标记：该字段的 ${auto} 应从数据中移除（由服务端自动生成 id）
_REMOVE = object()


def _process_auto(data, rules, list_rules=None):
    """
    ${auto} 占位符处理引擎（供三个业务函数内部调用）

    :param data: 待处理的原始数据字典（深拷贝处理，不修改调用方数据）
    :param rules: {字段名: 替换规则}，规则为以下三种之一：
        _REMOVE       -> 该字段的 ${auto} 从数据中移除
        可调用对象    -> 用 rules[key](unique_id) 的返回值替换
        常量          -> 直接用该常量替换
        未在 rules 中定义的字段统一替换为 "auto_{unique_id}"
    :param list_rules: {字段名: 替换值}，列表中值为 "${auto}" 的元素
                       用该替换值替代（如 department 列表中的根部门 id）
    :return: 处理后的新字典
    """
    if not isinstance(data, dict):
        return data

    result = copy.deepcopy(data)
    # 使用 uuid4 前 8 位生成唯一标识，保证并发/重复执行安全
    unique_id = uuid.uuid4().hex[:8]
    keys_to_remove = []

    for key, value in result.items():
        if value == "${auto}":
            if key in rules:
                rule = rules[key]
                if rule is _REMOVE:
                    keys_to_remove.append(key)
                elif callable(rule):
                    result[key] = rule(unique_id)
                else:
                    result[key] = rule
            else:
                result[key] = f"auto_{unique_id}"
        elif isinstance(value, dict):
            result[key] = _process_auto(value, rules, list_rules)
        elif isinstance(value, list):
            new_list = []
            for item in value:
                if isinstance(item, dict):
                    new_list.append(_process_auto(item, rules, list_rules))
                elif item == "${auto}" and list_rules and key in list_rules:
                    new_list.append(list_rules[key])
                else:
                    new_list.append(item)
            result[key] = new_list

    for key in keys_to_remove:
        result.pop(key, None)

    return result


def replace_auto_placeholder(data, root_dept_id=1):
    """
    部门模块：替换 data 中的 ${auto} 占位符
    - name -> test_部门_{uuid}
    - parentid -> 根部门ID（默认1）
    - id -> 移除该字段，由 API 自动生成
    """
    return _process_auto(data, rules={
        "name": lambda uid: f"test_部门_{uid}",
        "parentid": root_dept_id,
        "id": _REMOVE,
    })


def replace_auto_placeholder_user(data, root_dept_id=1):
    """
    用户模块：替换 data 中的 ${auto} 占位符
    - userid -> test_user_{uuid}
    - name -> test_用户_{uuid}
    - mobile -> 138 开头的 11 位手机号
    - email -> test_{uuid}@test.com
    - position -> test_pos_{uuid}
    - department 列表中的 "${auto}" -> 根部门ID
    """
    mobile_suffix = str(random.randint(100000000, 999999999))  # 8 位，加上 138 共 11 位
    return _process_auto(
        data,
        rules={
            "userid": lambda uid: f"test_user_{uid}",
            "name": lambda uid: f"test_用户_{uid}",
            "mobile": lambda uid: f"138{mobile_suffix}",
            "email": lambda uid: f"test_{uid}@test.com",
            "position": lambda uid: f"test_pos_{uid}",
        },
        list_rules={"department": root_dept_id},
    )


def replace_auto_placeholder_tag(data):
    """
    标签模块：替换 data 中的 ${auto} 占位符
    - tagname -> test_标签_{uuid}
    - tagid -> 移除该字段，由 API 自动生成
    """
    return _process_auto(data, rules={
        "tagname": lambda uid: f"test_标签_{uid}",
        "tagid": _REMOVE,
    })


# ============================================================
# Factory Fixture
#
# 设计说明：
# 1. 三个 factory 对外统一为 SimpleNamespace 形态：
#    factory.create(data) 创建资源、factory.created_ids 查看已创建资源。
#    department 额外提供 get_created()（查询创建时传入的完整数据），
#    因为部门用例需要 name 做后续查询。
# 2. 「创建成功后记录 id、测试结束批量清理」的流程是公共的，
#    抽取为 _cleanup_created；各业务如何调用接口、id 如何提取
#    是业务差异，保留在各 factory 内独立实现。
# ============================================================

def _cleanup_created(delete_func, created_ids, resource_name):
    """测试结束后批量清理已创建的资源，单条失败不影响其余清理"""
    if created_ids:
        log.info(f"[factory] 开始批量清理{resource_name}")
    for rid in created_ids:
        try:
            delete_func(rid)
            log.info(f"自动清理测试{resource_name}：{rid}")
        except Exception as e:
            log.warning(f"清理{resource_name} {rid} 失败: {e}")


@pytest.fixture
def department_factory(department_api):
    """
    部门资源 factory fixture：
    - create() 自动处理 ${auto} 占位符并创建部门
    - 创建成功自动记录部门 id，测试结束批量清理
    - get_created() 返回创建时使用的完整数据（含 name）
    """
    created_ids = []
    created_depts = []  # 保存创建时传入的数据，供后续用 name 查询

    def _create(data):
        processed_data = replace_auto_placeholder(data)

        res = department_api.create(processed_data)
        dep_id = res.json().get("id")

        if dep_id:
            created_ids.append(dep_id)
            created_depts.append({
                "id": dep_id,
                "name": processed_data.get("name"),
                "data": processed_data
            })

        return res

    def _get_created_dept(index=0):
        """获取已创建部门的信息（id / name / 原始数据）"""
        if index < len(created_depts):
            return created_depts[index]
        return None

    factory = SimpleNamespace(
        create=_create,
        get_created=_get_created_dept,
        created_ids=created_ids,
    )

    yield factory

    _cleanup_created(department_api.delete, created_ids, "部门")


@pytest.fixture
def user_factory(user_api):
    """
    用户资源 factory fixture：
    - create() 自动处理 ${auto} 占位符并创建用户
    - 创建成功自动记录 userid，测试结束批量清理
    - 创建的 userid 同时挂在响应对象的 created_userid 属性上，
      供 get/update/delete 用例直接获取
    """
    created_ids = []

    def _create(data):
        processed = replace_auto_placeholder_user(data)
        res = user_api.create(processed)
        if res.json().get("errcode") == 0 and processed.get("userid"):
            created_ids.append(processed["userid"])
        # 供 get/update/delete 用例获取本次创建的 userid
        setattr(res, "created_userid", processed.get("userid"))
        return res

    factory = SimpleNamespace(
        create=_create,
        created_ids=created_ids,
    )

    yield factory

    _cleanup_created(user_api.delete, created_ids, "用户")


@pytest.fixture
def tag_factory(tag_api):
    """
    标签资源 factory fixture：
    - create() 自动处理 ${auto} 占位符并创建标签
    - 创建成功自动记录 tagid，测试结束批量清理
    - 服务端返回的 tagid 同时挂在响应对象的 created_tagid 属性上，
      供 get/update/delete 用例直接获取
    """
    created_ids = []

    def _create(data):
        processed = replace_auto_placeholder_tag(data)
        res = tag_api.create(
            tagname=processed["tagname"],
            tagid=processed.get("tagid")
        )
        res_json = res.json()
        if res_json.get("errcode") == 0 and res_json.get("tagid") is not None:
            created_ids.append(res_json["tagid"])
        # 供 get/update/delete 用例获取本次创建的 tagid
        setattr(res, "created_tagid", res_json.get("tagid"))
        return res

    factory = SimpleNamespace(
        create=_create,
        created_ids=created_ids,
    )

    yield factory

    _cleanup_created(tag_api.delete, created_ids, "标签")
