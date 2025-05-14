import os
import time
import threading
import requests
from bs4 import BeautifulSoup
from flask import Flask

# Flask Web Service
app = Flask(__name__)

# Telegram Bot 設定
TELEGRAM_TOKEN = "7618181883:AAGN1IW8zFfUQ41I0NpxC0Z5ezmqktKBHfs"
CHAT_ID = "6126008495"

# 搜尋的關鍵字
KEYWORDS = ["RX100", "ZV1", "ZV-1", "LX10", "ZV-1M2", "ZV-1F"]

# 記錄已通知商品（避免重複）
notified_items = set()

# 發送 Telegram 訊息
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"發送 Telegram 訊息失敗：{e}")

# 爬蟲主邏輯
def check_dcview():
    url = "http://market.dcview.com/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        items = soup.select(".h5")

        for item in items:
            title = item.get_text().strip()
            link_tag = item.find_parent("a")
            href = link_tag.get("href") if link_tag else None
            time_tag = item.find_next("small")
            post_time = time_tag.get_text().strip() if time_tag else "（無時間）"

            if href:
                full_link = f"http://market.dcview.com{href}" if href.startswith("/") else href
                item_key = full_link

                if item_key in notified_items:
                    continue

                if any(keyword.lower() in title.lower() for keyword in KEYWORDS):
                    message = f"🆕 新上架商品: {title}\n🕒 商品價格: {post_time}\n🔗 連結: {full_link}"
                    send_telegram_message(message)
                    notified_items.add(item_key)
                    print(f"已通知商品：{item_key}")

    except Exception as e:
        print(f"爬蟲錯誤: {e}")

# 背景執行的爬蟲任務
def background_task():
    send_telegram_message("🔔 測試通知：dcview_notify 啟動成功")
    while True:
        check_dcview()
        time.sleep(10)

# Flask 根目錄顯示狀態
@app.route("/")
def index():
    return "🚀 dcview_notify 正在運行中..."

# 啟動伺服器
if __name__ == "__main__":
    # 啟動背景爬蟲執行緒
    threading.Thread(target=background_task, daemon=True).start()

    # 取得 Render 所提供的 PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
