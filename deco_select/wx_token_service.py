import requests
import logging
import threading
import time
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

def refresh_once():
    url = (
        "https://api.weixin.qq.com/cgi-bin/token"
        f"?grant_type=client_credential&appid={settings.WECHAT_APPID}&secret={settings.WECHAT_SECRET}"
    )
    try:
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if "access_token" in data:
            token = data["access_token"]
            expires_in = data.get("expires_in", 7200)
            cache.set("wx_access_token", token, expires_in - 300)
            print(f"[微信token] 启动时获取成功: {token[:20]}...  有效期 {expires_in}s")
        else:
            print(f"[微信token] 启动时获取失败: {data}")
    except Exception as e:
        print(f"[微信token] 启动时异常: {e}")

def refresh_loop():
    """循环定时刷新"""
    while True:
        time.sleep(3600)   # 每小时再刷新
        refresh_once()

def start_wx_token_thread():
    """Django 启动时执行：先刷一次，然后后台循环刷新"""
    refresh_once()  # ✅ 立即先刷新一次
    t = threading.Thread(target=refresh_loop, daemon=True)
    t.start()
