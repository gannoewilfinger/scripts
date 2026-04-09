#!/usr/bin/env python3
"""
Smartproxy IP质量守护服务
常驻运行，每60秒检测IP是否变化，变了就检测质量

轻量：只有IP变化时才调用ip-api检测质量
"""
import urllib.request
import json
import os
import time
import re
import threading

CHECK_INTERVAL = 60  # 每60秒检测一次IP是否变化
CLASH_CONFIG = os.path.expanduser("~/.config/clash.meta/hk-proxy.yaml")
CLASH_API = "http://127.0.0.1:9091"
GITHUB_PROXY = "http://127.0.0.1:7892"
STATE_FILE = os.path.expanduser("~/.config/clash.meta/ip-guard-state")
LOG_FILE = os.path.expanduser("~/.config/clash.meta/ip-guard.log")
MAX_ATTEMPTS = 20

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")
    except:
        pass

def get_current_ip():
    """通过 GitHub 代理获取出口 IP（轻量操作）"""
    try:
        proxy = urllib.request.ProxyHandler({"http": GITHUB_PROXY, "https": GITHUB_PROXY})
        opener = urllib.request.build_opener(proxy)
        req = urllib.request.Request("https://api.ipify.org", headers={"User-Agent": "curl/7.0"})
        with opener.open(req, timeout=10) as resp:
            return resp.read().decode().strip()
    except:
        return None

def check_ip_quality(ip):
    """检测IP是否干净"""
    try:
        url = f"http://ip-api.com/json/{ip}?fields=proxy,hosting,isp"
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            is_clean = data.get("proxy") == False and data.get("hosting") == False
            isp = data.get("isp", "Unknown")
            return is_clean, isp
    except:
        return False, "Error"

def get_saved_ip():
    try:
        with open(STATE_FILE) as f:
            parts = f.read().strip().split(":")
            return parts[1] if len(parts) > 1 else ""
    except:
        return ""

def save_state(ip, isp):
    with open(STATE_FILE, "w") as f:
        f.write(f"{int(time.time())}:{ip}:{isp}")

def rotate_session():
    """换 Smartproxy session"""
    import secrets
    new_session = secrets.token_hex(8)
    
    with open(CLASH_CONFIG) as f:
        content = f.read()
    
    new_content = re.sub(r"session-[a-zA-Z0-9]+", f"session-{new_session}", content)
    
    with open(CLASH_CONFIG, "w") as f:
        f.write(new_content)
    
    try:
        req = urllib.request.Request(
            f"{CLASH_API}/configs?force=true",
            method="PUT",
            data=json.dumps({"path": CLASH_CONFIG}).encode(),
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=5)
    except:
        pass
    
    time.sleep(3)

def find_clean_ip():
    """轮换直到找到干净IP"""
    log("🔄 寻找干净IP...")
    for i in range(1, MAX_ATTEMPTS + 1):
        rotate_session()
        ip = get_current_ip()
        if not ip:
            log(f"  [{i}] 连接失败")
            continue
        
        is_clean, isp = check_ip_quality(ip)
        if is_clean:
            log(f"✅ 第{i}次: {ip} ({isp})")
            save_state(ip, isp)
            os.system(f'osascript -e \'display notification "{ip} ({isp})" with title "✅ 干净IP"\' 2>/dev/null')
            return True
        log(f"  [{i}] {ip} 脏")
    
    log(f"❌ {MAX_ATTEMPTS}次未找到")
    return False

def check_and_fix():
    """主检测逻辑：IP变化 → 检测质量 → 脏就换"""
    current_ip = get_current_ip()
    if not current_ip:
        return  # 网络问题，跳过这轮
    
    saved_ip = get_saved_ip()
    
    # IP没变，跳过
    if current_ip == saved_ip:
        return
    
    # IP变了
    log(f"🔍 IP变化: {saved_ip} → {current_ip}")
    is_clean, isp = check_ip_quality(current_ip)
    
    if is_clean:
        log(f"✅ 新IP干净: {current_ip} ({isp})")
        save_state(current_ip, isp)
        return
    
    # 脏了，换
    log(f"⚠️ 新IP脏，开始轮换")
    find_clean_ip()

def main():
    log(f"━━━ IP守护服务启动 (每{CHECK_INTERVAL}秒检测) ━━━")
    
    # 启动时检测一次
    current_ip = get_current_ip()
    if current_ip:
        is_clean, isp = check_ip_quality(current_ip)
        if is_clean:
            log(f"✅ 启动IP干净: {current_ip} ({isp})")
            save_state(current_ip, isp)
        else:
            log(f"⚠️ 启动IP脏，开始轮换")
            find_clean_ip()
    
    # 循环检测
    while True:
        time.sleep(CHECK_INTERVAL)
        try:
            check_and_fix()
        except Exception as e:
            log(f"⚠️ 检测异常: {e}")

if __name__ == "__main__":
    main()
