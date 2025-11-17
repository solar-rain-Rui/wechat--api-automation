
from frame.apis.contacts.departments import Departments
from frame.apis.contacts.users import Users
from frame.apis.contacts.tags import Tags
from frame.common.tools import load_yaml
from frame.common.logger import log


def prepare_departments_data():
    """准备部门模块测试数据"""
    dep = Departments()
    exist_res = dep.get()
    exist_ids = [d["id"] for d in exist_res.json().get("department", [])]

    try:
        cases = load_yaml("datas/departments.yaml")
    except FileNotFoundError:
        log.warning("未找到部门测试数据文件，跳过部门数据准备")
        return

    for key in ["delete_department", "update_department", "get_department"]:
        for case in cases.get(key, []):
            dep_id = case["data"].get("id")
            # 跳过根部门、缺少id的用例
            if not dep_id or dep_id == 1:
                continue
            # 如果yaml指定的id不存在，则创建
            if dep_id not in exist_ids:
                create_res = dep.create({
                    "name": f"预置_{key}_{dep_id}",
                    "parentid": 1
                })
                new_id = create_res.json().get("id")
                log.info(f"✅ 为 {key} 预置部门: YAML写id={dep_id} 实际id={new_id}")


def prepare_users_data():
    """准备用户模块测试数据（最简版本）"""
    user_api = Users()

    try:
        cases = load_yaml("datas/users.yaml")
    except FileNotFoundError:
        log.warning("未找到用户测试数据文件，跳过用户数据准备")
        return

    # 对 delete_user / update_user / get_user 统一准备
    for key in ["delete_user", "update_user", "get_user"]:
        for case in cases.get(key, []):
            userid = case["data"].get("userid")
            if not userid:
                continue

            # 判断该用户是否存在
            res = user_api.get(userid).json()
            if res.get("errcode") == 60111:
                # 用户不存在 → 创建一个
                create_data = {
                    "userid": userid,
                    "name": f"预置_{key}_{userid}",
                    "department": [1]     # 写死一个必定存在的部门 ID
                }
                create_res = user_api.create(create_data).json()
                log.info(f"预置用户 {userid}：{create_res}")




def prepare_tags_data():
    """准备标签模块测试数据"""
    tag_api = Tags()
    try:
        cases = load_yaml("datas/tags.yaml")
    except FileNotFoundError:
        log.warning("未找到标签测试数据文件，跳过标签数据准备")
        return

    for key in ["delete_tag", "update_tag", "get_tag"]:
        for case in cases.get(key, []):
            tagid = case["data"].get("tagid")
            if not tagid:
                continue
            get_res = tag_api.get(tagid)
            if get_res.json().get("errcode") == 40068:  # 标签不存在
                create_data = {"tagid": tagid, "tagname": f"预置_{key}_{tagid}"}
                create_res = tag_api.create(**create_data)
                log.info(f"✅ 为 {key} 预置标签: {create_res.json()}")


def prepare_all_test_data(departments=True, users=True, tags=True):
    """统一准备所有模块测试数据"""
    if departments:
        prepare_departments_data()
    else:
        log.info("跳过部门数据准备")
    if users:
        prepare_users_data()
    else:
        log.info("跳过用户数据准备")
    if tags:
        prepare_tags_data()
    else:
        log.info("跳过标签数据准备")
    log.info("========== 测试数据准备完成 ==========")
