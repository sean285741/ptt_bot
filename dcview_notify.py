import requests
from bs4 import BeautifulSoup
import time

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
    requests.post(url, data=payload)

# 檢查 DCView 新上架商品
def check_dcview():
    url = "http://market.dcview.com/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

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

            # 使用商品的 URL 來唯一識別商品
            if href:
                full_link = f"http://market.dcview.com{href}" if href.startswith("/") else href

                item_key = full_link  # 使用商品的 URL 作為唯一識別

                if item_key in notified_items:
                    continue  # 已通知過

                if any(keyword.lower() in title.lower() for keyword in KEYWORDS):
                    message = f"🆕 新上架商品: {title}\n🕒 商品價格: {post_time}\n🔗 連結: {full_link}"
                    send_telegram_message(message)
                    notified_items.add(item_key)
                    print(f"已通知商品：{item_key}")

    except Exception as e:
        print(f"請求錯誤: {e}")

# 主程式
def main():
    print("開始監控 DCView 新上架商品...")
    send_telegram_message("🔔 測試通知：dcview_notify 啟動成功")
    while True:
        check_dcview()
        time.sleep(10)  # 每 10 秒檢查一次

if __name__ == "__main__":
    main()
