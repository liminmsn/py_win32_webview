import requests
from typing import TypedDict, Literal
# ============================================================
# Session
# ============================================================
session = requests.Session()
# ============================================================
# HttpValue
# ============================================================
class HttpValue(TypedDict, total=False):
    url: str
    headers: dict[str, str]
    method: Literal[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
    ]
    body: dict[str, str]

# ============================================================
# Send
# ============================================================
def send(value: HttpValue) -> dict:
    """
    根据 HttpValue 发起 HTTP 请求。

    返回统一结构：

    {
        "ok": bool,
        "status": int,
        "url": str,
        "headers": dict,
        "body": str,
        "error": str | None
    }
    """

    url = value.get("url", "")
    method = value.get("method", "GET").upper()
    headers = value.get("headers") or {}
    body = value.get("body") or {}

    if not url:
        return {
            "ok": False,
            "status": 0,
            "url": "",
            "headers": {},
            "body": "",
            "error": "URL 不能为空",
        }

    try:
        # --------------------------------------------------------
        # 发起请求
        # --------------------------------------------------------
        response = session.request(
            method=method,
            url=url,
            headers=headers,
            data=body,
            timeout=15,
            allow_redirects=True,
        )
        # --------------------------------------------------------
        # 编码
        # --------------------------------------------------------
        response.encoding = "utf-8"
        # --------------------------------------------------------
        # HTTP 错误
        #
        # 不再使用 raise_for_status()，
        # 直接统一转换成返回值。
        # --------------------------------------------------------
        if not response.ok:
            return {
                "ok": False,
                "status": response.status_code,
                "url": response.url,
                "headers": dict(response.headers),
                "body": response.text,
                "error": f"HTTP {response.status_code}",
            }
        # --------------------------------------------------------
        # 成功
        # --------------------------------------------------------
        return {
            "ok": True,
            "status": response.status_code,
            "url": response.url,
            "headers": dict(response.headers),
            "body": response.text,
            "error": None,
        }
    # ------------------------------------------------------------
    # 请求超时
    # ------------------------------------------------------------
    except requests.exceptions.Timeout:
        return {
            "ok": False,
            "status": 0,
            "url": url,
            "headers": {},
            "body": "",
            "error": "请求超时",
        }
    # ------------------------------------------------------------
    # 连接失败
    # ------------------------------------------------------------
    except requests.exceptions.ConnectionError as e:
        return {
            "ok": False,
            "status": 0,
            "url": url,
            "headers": {},
            "body": "",
            "error": f"连接失败：{e}",
        }
    # ------------------------------------------------------------
    # 其他 Requests 异常
    # ------------------------------------------------------------
    except requests.exceptions.RequestException as e:
        return {
            "ok": False,
            "status": 0,
            "url": url,
            "headers": {},
            "body": "",
            "error": str(e),
        }
    # ------------------------------------------------------------
    # 其他未知异常
    # ------------------------------------------------------------
    except Exception as e:
        return {
            "ok": False,
            "status": 0,
            "url": url,
            "headers": {},
            "body": "",
            "error": f"未知错误：{e}",
        }