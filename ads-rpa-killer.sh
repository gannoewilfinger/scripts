#!/bin/bash
# ADS RPA自动关闭守护脚本
# 监控ADS进程，发现RPA模块自动关闭

LOG_FILE="$HOME/.config/ads-rpa-killer.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "守护脚本启动"

while true; do
    # 检查ADS是否在运行
    if pgrep -f "AdsPower Global" > /dev/null; then
        # 检查RPA是否在运行
        RPA_PIDS=$(pgrep -f "rpa.*min.js")
        if [ -n "$RPA_PIDS" ]; then
            pkill -f "rpa.min.js" 2>/dev/null
            pkill -f "rpa_plus.min.js" 2>/dev/null
            log "已关闭RPA进程: $RPA_PIDS"
        fi
    fi
    sleep 5  # 每5秒检查一次
done
