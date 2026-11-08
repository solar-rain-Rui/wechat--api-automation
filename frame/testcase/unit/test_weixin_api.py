"""
WeComApi（企业微信 Token 层）专项单元测试

验证目标：
1. 正常请求不触发任何刷新重试
2. token 失效（40014/42001）→ 强制刷新 → 回写实例 → 重试一次
3. 重试最多 1 次，且完全复用通用发送逻辑（代理配置一致）
4. 重试不原地修改调用方传入的参数字典
5. params 为 None / 缺失时重试自动补齐
6. 非 JSON 响应不做失效判断，直接返回
7. 非 token 失效错误码（如 IP 白名单 60020）不触发重试

全部通过 monkeypatch 替换 requests.request 与 fetch_token，不依赖真实企业微信环境。
"""
import copy

import pytest
import requests

import frame.apis.weixin_base as wecom_module
from frame.apis.weixin_base import WeComApi


class FakeResponse:
    """模拟 requests.Response，仅实现本项目用到的最小接口"""

    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json_data = json_data
        self.text = text if text else str(json_data)

    def json(self):
        if self._json_data is not None:
            return self._json_data
        raise ValueError("No JSON object could be decoded")


@pytest.fixture
def api():
    return WeComApi(token="old_token")


def _patch_request(monkeypatch, responses):
    """按调用顺序依次返回 responses，并记录每次请求的入参"""
    calls = []

    def fake_request(**kwargs):
        calls.append(kwargs)
        return responses[len(calls) - 1]

    monkeypatch.setattr(requests, "request", fake_request)
    return calls


def _patch_fetch_token(monkeypatch, token="new_token"):
    """替换 fetch_token，记录是否被强制刷新"""
    fetch_calls = []

    def fake_fetch_token(force=False):
        fetch_calls.append(force)
        return token

    monkeypatch.setattr(wecom_module, "fetch_token", fake_fetch_token)
    return fetch_calls


def test_normal_response_no_refresh_no_retry(api, monkeypatch):
    """errcode=0 的正常响应：不刷新 token、不重试"""
    calls = _patch_request(monkeypatch, [FakeResponse(json_data={"errcode": 0, "errmsg": "ok"})])
    fetch_calls = _patch_fetch_token(monkeypatch)

    r = api.send_api({"method": "GET", "url": "http://x", "params": {"access_token": "old_token"}})

    assert len(calls) == 1
    assert fetch_calls == []
    assert r.json()["errcode"] == 0


def test_token_expired_refresh_and_retry_once(api, monkeypatch):
    """40014 → 强制刷新 token → 回写实例 → 用新 token 重试一次"""
    calls = _patch_request(monkeypatch, [
        FakeResponse(json_data={"errcode": 40014, "errmsg": "invalid access_token"}),
        FakeResponse(json_data={"errcode": 0, "errmsg": "ok"}),
    ])
    fetch_calls = _patch_fetch_token(monkeypatch)

    original = {
        "method": "GET",
        "url": "http://x",
        "params": {"access_token": "old_token", "id": 5},
    }
    snapshot = copy.deepcopy(original)

    r = api.send_api(original)

    assert r.json()["errcode"] == 0
    # 最多重试 1 次（共 2 次请求）
    assert len(calls) == 2
    # 刷新为强制模式
    assert fetch_calls == [True]
    # 新 token 已回写实例，后续请求直接使用
    assert api.token == "new_token"
    # 重试请求携带新 token，其他参数原样保留
    assert calls[1]["params"]["access_token"] == "new_token"
    assert calls[1]["params"]["id"] == 5
    # 重试完全复用通用发送逻辑：代理禁用配置一致
    assert calls[1]["proxies"] == {"http": None, "https": None}
    # 调用方传入的原始字典未被原地修改
    assert original == snapshot


def test_retry_only_once_even_if_still_expired(api, monkeypatch):
    """重试后仍失效也不再重试，最多 1 次，防止请求风暴"""
    calls = _patch_request(monkeypatch, [
        FakeResponse(json_data={"errcode": 42001}),
        FakeResponse(json_data={"errcode": 42001}),
    ])
    _patch_fetch_token(monkeypatch)

    r = api.send_api({"method": "GET", "url": "http://x", "params": {"access_token": "old_token"}})

    assert len(calls) == 2
    assert r.json()["errcode"] == 42001


@pytest.mark.parametrize("errcode", [40014, 42001])
def test_both_expired_codes_trigger_refresh(api, monkeypatch, errcode):
    """40014 与 42001 两种失效码都应触发刷新重试"""
    calls = _patch_request(monkeypatch, [
        FakeResponse(json_data={"errcode": errcode}),
        FakeResponse(json_data={"errcode": 0}),
    ])
    _patch_fetch_token(monkeypatch)

    r = api.send_api({"method": "GET", "url": "http://x", "params": {"access_token": "old_token"}})

    assert len(calls) == 2
    assert r.json()["errcode"] == 0


def test_other_error_no_retry(api, monkeypatch):
    """非 token 失效错误码（如 IP 白名单 60020）不触发刷新重试"""
    calls = _patch_request(monkeypatch, [FakeResponse(json_data={"errcode": 60020})])
    fetch_calls = _patch_fetch_token(monkeypatch)

    r = api.send_api({"method": "GET", "url": "http://x", "params": {"access_token": "old_token"}})

    assert len(calls) == 1
    assert fetch_calls == []
    assert r.json()["errcode"] == 60020


def test_non_json_response_no_retry(api, monkeypatch):
    """响应不是 JSON 时无法判断失效，直接原样返回，不刷新不重试"""
    calls = _patch_request(monkeypatch, [FakeResponse(status_code=200, text="<html>gateway error</html>")])
    fetch_calls = _patch_fetch_token(monkeypatch)

    r = api.send_api({"method": "GET", "url": "http://x"})

    assert len(calls) == 1
    assert fetch_calls == []
    assert r.text == "<html>gateway error</html>"


def test_json_not_dict_no_retry(api, monkeypatch):
    """响应 JSON 是列表等非字典结构时不崩溃、不重试"""
    calls = _patch_request(monkeypatch, [FakeResponse(json_data=[1, 2, 3])])
    fetch_calls = _patch_fetch_token(monkeypatch)

    r = api.send_api({"method": "GET", "url": "http://x"})

    assert len(calls) == 1
    assert fetch_calls == []
    assert r.json() == [1, 2, 3]


def test_retry_with_params_none(api, monkeypatch):
    """请求不含 params 键（值为 None 场景）：重试时自动补齐参数字典"""
    calls = _patch_request(monkeypatch, [
        FakeResponse(json_data={"errcode": 40014}),
        FakeResponse(json_data={"errcode": 0}),
    ])
    _patch_fetch_token(monkeypatch)

    r = api.send_api({"method": "POST", "url": "http://x", "json": {"a": 1}})

    assert r.json()["errcode"] == 0
    assert calls[1]["params"] == {"access_token": "new_token"}
    # 原 json 请求体原样保留
    assert calls[1]["json"] == {"a": 1}


def test_expired_code_and_stale_token_not_leaked_to_retry_params(api, monkeypatch):
    """重试 params 中不得残留旧 token"""
    calls = _patch_request(monkeypatch, [
        FakeResponse(json_data={"errcode": 42001}),
        FakeResponse(json_data={"errcode": 0}),
    ])
    _patch_fetch_token(monkeypatch)

    api.send_api({"method": "GET", "url": "http://x", "params": {"access_token": "old_token", "tagid": 9}})

    assert calls[1]["params"] == {"access_token": "new_token", "tagid": 9}
