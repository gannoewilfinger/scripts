#!/bin/bash
# Smartproxy IP质量守护
# 核心逻辑：IP变化 → 检测质量 → 脏就换

CLASH_CONFIG="$HOME/.config/clash.meta/hk-proxy.yaml"
CLASH_API="http://127.0.0.1:9091"
GITHUB_PROXY="http://127.0.0.1:7892"
LOG_FILE="$HOME/.config/clash.meta/ip-guard.log"
STATE_FILE="$HOME/.config/clash.meta/ip-guard-state"
MAX_ATTEMPTS=20

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    echo "$1"
}

check_clash() {
    curl -s --max-time 3 "$CLASH_API/version" > /dev/null 2>&1
}

get_current_ip() {
    curl -s --max-time 10 --proxy "$GITHUB_PROXY" https://api.ipify.org 2>/dev/null
}

check_ip_quality() {
    local ip="$1"
    local q=$(curl -s --max-time 5 "http://ip-api.com/json/${ip}?fields=proxy,hosting,isp" 2>/dev/null)
    local p=$(echo "$q" | grep -o '"proxy":[^,}]*' | cut -d: -f2)
    local h=$(echo "$q" | grep -o '"hosting":[^,}]*' | cut -d: -f2)
    local isp=$(echo "$q" | grep -o '"isp":"[^"]*"' | cut -d'"' -f4)
    
    [ "$p" = "false" ] && [ "$h" = "false" ] && echo "CLEAN:$isp" || echo "DIRTY:p=$p,h=$h"
}

rotate_session() {
    local s=$(openssl rand -hex 8)
    sed -i '' "s/session-[a-zA-Z0-9]*/session-${s}/" "$CLASH_CONFIG"
    curl -s -X PUT "$CLASH_API/configs?force=true" -H "Content-Type: application/json" -d "{\"path\":\"$CLASH_CONFIG\"}" >/dev/null 2>&1
    sleep 3
}

get_saved_ip() {
    [ -f "$STATE_FILE" ] && cut -d: -f2 "$STATE_FILE" || echo ""
}

save_state() {
    echo "$(date +%s):$1:$2" > "$STATE_FILE"
}

find_clean_ip() {
    log "🔄 寻找干净IP..."
    for i in $(seq 1 $MAX_ATTEMPTS); do
        rotate_session
        local ip=$(get_current_ip)
        [ -z "$ip" ] && { log "  [$i] 连接失败"; sleep 1; continue; }
        
        local result=$(check_ip_quality "$ip")
        if [ "${result%%:*}" = "CLEAN" ]; then
            local isp="${result#*:}"
            log "✅ 第${i}次: $ip ($isp)"
            save_state "$ip" "$isp"
            osascript -e "display notification \"$ip ($isp)\" with title \"✅ 干净IP\"" 2>/dev/null
            return 0
        fi
        log "  [$i] $ip $result"
        sleep 1
    done
    log "❌ ${MAX_ATTEMPTS}次未找到"
    return 1
}

main() {
    log "━━━ IP守护 ━━━"
    check_clash || { log "⚠️ Clash未运行"; exit 1; }
    
    local current_ip=$(get_current_ip)
    [ -z "$current_ip" ] && { log "⚠️ 无法获取IP"; exit 1; }
    
    local saved_ip=$(get_saved_ip)
    
    # IP没变 → 跳过
    if [ "$current_ip" = "$saved_ip" ]; then
        log "✅ IP未变: $current_ip"
        exit 0
    fi
    
    # IP变了 → 检查质量
    log "🔍 IP变化: $saved_ip → $current_ip"
    local result=$(check_ip_quality "$current_ip")
    
    if [ "${result%%:*}" = "CLEAN" ]; then
        local isp="${result#*:}"
        log "✅ 新IP干净: $current_ip ($isp)"
        save_state "$current_ip" "$isp"
        exit 0
    fi
    
    # 脏了 → 换
    log "⚠️ 新IP脏: $result"
    find_clean_ip
}

main
