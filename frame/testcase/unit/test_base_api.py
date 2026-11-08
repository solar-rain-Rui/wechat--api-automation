"""
BaseApi（通用 HTTP 层）单元测试

验证目标：
1. 只做 HTTP 转发：requests.request 收到原始参数，返回原始 Response 对象
2. 不假设响应是 JSON：非 JSON 响应不报错
3. 不依赖任何企业微信模块（检查源码级隔离）
4. 日志脱敏：URL 中的 access_token 不以明文进入日志

全部通过 monkeypatch 替换 requests.request，不产生真实网络请求。
"""
import json as json_lib

import pytest
import requests

from frame.apis.base_api import BaseApi, _mask_url


class FakeResponse:
    """模拟 requests.Response，仅实现本项目用到的最小接口"""

    def __init__(self, status_code=200, text="", json_data=None):
        self.status_code = status_code
        self.text = text
        self._json_data = json_data

    def json(self):
        if self._json_data is not None:
            return self._json_data
        return json_lib.loads(self.text)


@pytest.fixture
def api():
    return BaseApi(token="fake_token")


def test_send_api_forwards_request_and_returns_response(api, monkeypatch):
    """BaseApi 应把 req 原样转发给 requests.request，并原样返回 Response"""
    captured = {}

    def fake_request(**kwargs):
        captured.update(kwargs)
        return FakeResponse(status_code=200, text="ok")

    monkeypatch.setattr(requests, "request", fake_request)

    req = {"method": "GET", "url": "http://httpbin.org/get", "params": {"a": 1}}
    r = api.send_api(req)

    assert r.status_code == 200
    assert r.text == "ok"
    assert captured["method"] == "GET"
    assert captured["url"] == "http://httpbin.org/get"
    assert captured["params"] == {"a": 1}
    # 代理禁用配置应始终存在
    assert captured["proxies"] == {"http": None, "https": None}


def test_send_api_supports_non_json_response(api, monkeypatch):
    """响应为 HTML 等非 JSON 内容时不应抛异常，文本原样保留"""
    monkeypatch.setattr(
        requests, "request",
        lambda **kw: FakeResponse(status_code=404, text="<html>not json</html>")
    )
    r = api.send_api({"method": "GET", "url": "http://httpbin.org/404"})

    assert r.status_code == 404
    assert r.text == "<html>not json</html>"


def test_base_api_has_no_wecom_dependency():
    """通用层源码中不得出现任何企业微信专属逻辑（源码级隔离守护）"""
    import frame.apis.base_api as base_api_module
    with open(base_api_module.__file__, encoding="utf-8") as f:
        source = f.read()

    assert "token_get" not in source, "BaseApi 不得导入企业微信 token 模块"
    assert "40014" not in source and "42001" not in source, "BaseApi 不得包含企业微信错误码"
    assert "errcode" not in source, "BaseApi 不得解析业务错误码"


def test_mask_url_hides_access_token():
    """日志脱敏函数：access_token 参数值应被替换为 ***"""
    masked = _mask_url("https://qyapi.weixin.qq.com/a/b?access_token=SECRET123&id=5")
    assert "SECRET123" not in masked
    assert "access_token=***" in masked
    assert "id=5" in masked

    # URL 中无 token 时原样返回
    assert _mask_url("http://x/y?foo=1") == "http://x/y?foo=1"
