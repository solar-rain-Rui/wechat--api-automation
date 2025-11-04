import pytest
from frame.apis.contacts.tags import Tags

@pytest.fixture(scope="function")
def tag_api():
    """提供标签接口实例"""
    return Tags()

@pytest.fixture(scope="function")
def temp_tag(tag_api):
    """创建临时标签"""
    res = tag_api.create(f"临时标签")
    tagid = res.json().get("tagid")
    yield tagid
    tag_api.delete(tagid)
