import requests
from typing import TypedDict, Literal

class HttpValue(TypedDict):
    url:str
    headers:dict[str,str]
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"]

def handle(value: HttpValue):
    print(value["url"])
    print(value["method"])
    print(value["headers"])

def send(value: HttpValue) -> dict:
    """根据 HttpValue 发请求，返回统一结构的响应。"""

    url = value["url"]
    method = value["method"].upper()
    headers = value.get("headers") or {}

    try:
        r = requests.request(method=method,url=url,headers=headers,timeout=15)
        r.raise_for_status()
    except requests.exceptions.Timeout:
        return {"ok": False, "status": 0, "body": "", "error": "请求超时"}
    except requests.exceptions.ConnectionError as e:
        return {"ok": False, "status": 0, "body": "", "error": f"连不上：{e}"}
    except requests.exceptions.RequestException as e:
            return {"ok": False, "status": 0, "body": "", "error": str(e)}
    except requests.exceptions.HTTPError as e:
        return {
            "ok": False,
            "status": e.response.status_code,
            "body": e.response.text,
            "error": f"HTTP {e.response.status_code}",
        }
    
    r.encoding = "utf-8"
    return {
        "ok": True,
        "status": r.status_code,
        "headers": dict(r.headers),
        "body": r.text,
        "error": None,
    }
