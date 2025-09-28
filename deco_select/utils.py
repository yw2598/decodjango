import requests
from django.core.cache import cache
from django.conf import settings
from .models import WechatUser

def wechat_code2session(code: str) -> dict:
    """
    调用微信 jscode2session，换取 openid
    https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/user-login/code2Session.html
    """
    print(code)
    url = (
        "https://api.weixin.qq.com/sns/jscode2session"
        f"?appid={settings.WECHAT_APPID}"
        f"&secret={settings.WECHAT_SECRET}"
        f"&js_code={code}"
        f"&grant_type=authorization_code"
    )
    resp = requests.get(url, timeout=5)
    print(resp.json())
    return resp.json()


def login_by_code(code: str) -> dict:
    """
    登录逻辑：
    - 用 code 换 openid
    - 验证数据库是否有用户
    """
    data = wechat_code2session(code)
    if "openid" not in data:
        return {"success": False, "msg": data}

    openid = data["openid"]

    try:
        user = WechatUser.objects.get(openid=openid)
        return {
            "success": True,
            "msg": "登录成功",
            "openid": user.openid,
            "phone_number": user.phone_number,
        }
    except WechatUser.DoesNotExist:
        return {"success": False, "msg": "用户未注册", "openid": openid}



def get_access_token():
    """从缓存里取 access_token"""
    return cache.get("wx_access_token")


def wechat_get_phone_number(phone_code: str) -> dict:
    """
    根据小程序端传来的 phone_code 获取手机号
    """
    token = get_access_token()
    if not token:
        return {"success": False, "msg": "access_token 不存在，请检查定时任务"}

    url = f"https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token={token}"
    resp = requests.post(url, json={"code": phone_code}, timeout=5)
    data = resp.json()

    if data.get("errcode") == 0:
        phone = data["phone_info"]["purePhoneNumber"]
        return {"success": True, "phone_number": phone}
    else:
        return {"success": False, "msg": data}

def register_user(code: str, phone_code: str, username: str) -> dict:
    """
    注册逻辑：
    - 用 code 换 openid
    - 用 phone_code 解密手机号
    - 保存到数据库
    """
    # 第一步：换 openid
    data = wechat_code2session(code)
    if "openid" not in data:
        return {"success": False, "msg": data}
    openid = data["openid"]

    # 第二步：解密手机号
    phone_res = wechat_get_phone_number(phone_code)
    if not phone_res.get("success"):
        return {"success": False, "msg": phone_res.get("msg")}
    phone_number = phone_res["phone_number"]

    # 第三步：检查数据库
    if WechatUser.objects.filter(openid=openid).exists():
        return {"success": False, "msg": "该 openid 已注册"}

    if WechatUser.objects.filter(phone_number=phone_number).exists():
        return {"success": False, "msg": "该手机号已注册"}

    # 第四步：创建用户
    user = WechatUser.objects.create(
        openid=openid,
        phone_number=phone_number,
        username=username,
    )

    return {
        "success": True,
        "msg": "注册成功",
        "user": {
            "id": user.id,
            "openid": user.openid,
            "phone_number": user.phone_number,
            "username": user.username,
        },
    }
