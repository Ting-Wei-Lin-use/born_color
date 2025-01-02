# 載入 Selenium 相關模組
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import urllib.request as req
import os
import requests
import json
import time


# Chrome Serivce與連線網址設定
service = Service(r"C:\Users\TMP214\Desktop\Topics\chromedriver.exe")
driver = webdriver.Chrome(service=service)
women_clothes_url = "https://d.uniqlo.com/tw/p/search/products/by-category" # 女裝上衣API(名稱by-category)，內容包含女裝上衣所有商品內容的json
driver.get(women_clothes_url)
time.sleep(10)
print("網頁加載完成")

# 模擬滾動頁面並獲取request_data
def scroll_and_get_data():
    page = 1
    all_request_data = []  # 儲存讀取資料的list

    while True:
        print(f"正在加載第 {page} 頁")
        
        # Request Data：發送請求包含的附加資訊Request Payload(veiw source點開後複製)
        request_data = {
            "url": "/tw/zh_TW/c/all_women-tops.html",
            "pageInfo": {"page": page, "pageSize": 24},  # 隨網頁滾動載入新的page，同時取得新的商品項目
            "belongTo": "pc",
            "rank": "overall",
            "priceRange": {"low": 0, "high": 0},
            "color": [],
            "size": [],
            "identity": [],
            "exist": [],
            "categoryCode": "all_women-tops",
            "searchFlag": False,
            "description": "",
            "stockFilter": "warehouse"
        }

        # 發送請求，將結果讀出(Request Payload為json)且以utf-8解碼
        request = req.Request(women_clothes_url, headers={
            "Content-type": "application/json",  # API請求的資料格式
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }, data=json.dumps(request_data).encode("utf-8"))

        # 發送請求，讀取結果
        with req.urlopen(request) as response:
            result = response.read().decode("utf-8")
            result = json.loads(result)  # 解析JSON結果
            
            # 檢查是否有商品資料
            items = result["resp"][0]["productList"]
            if not items:
                print("已經沒有更多商品，結束抓取。")
                break
            
            # 儲存每次獲取的資料
            all_request_data.append(result)

        # 模擬滾動操作，等待網頁加載
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # 等待新內容加載，根據需要調整時間

        page += 1  # 換頁
    return all_request_data

# 呼叫滾動與資料抓取的函數
all_data = scroll_and_get_data()
# 儲存資料的字典
output_data = {}

# 印出獲取的所有資料
for data in all_data:
    items = data["resp"][0]["productList"]
    for item in items:
        clothingId = item["code"]  # UQ商品編號：如472150
        colorIdList = item["colorNums"]  # colorId 變成一個列表
        # colorId = item["colorNums"]  # UQ顏色編號：如COL01
        colorPic = item["colorPic"]  # UQ衣服圖片網址(不含網域)：如/hmall/test/u0000000020259/sku/225/COL01.jpg
        imageUrl = [f"https://www.uniqlo.com/tw{COL}" for COL in colorPic]
        chipPic = item["chipPic"]  # UQ色塊網址(不含網域)：如/hmall/test/u0000000020259/chip/22/COL09.jpg
        color_block_url = [f"https://www.uniqlo.com/tw{CHIP}" for CHIP in chipPic]
        clothes_category = []  # UQ分類：如all_women-tops
        for product in item["categoryCode"]:  # 各衣服在API架構中index不同，故設定條件篩選catrgory
            if product == "all_women-tops":
                clothes_category.append(product)
        productCode = item["productCode"]  # UQ商品代號：如u0000000050507
        UniqloUrl = f"https://www.uniqlo.com/tw/zh_TW/product-detail.html?productCode={productCode}"

        print(f"{clothingId}")
        print(imageUrl)
        print(f"{colorIdList}")
        print(color_block_url)
        print(f"{clothes_category}")
        print(UniqloUrl)
        print("-" * 40)

        # 遍歷 colorIdList 中的每個顏色，將每個顏色作為字典的鍵
        for colorId in colorIdList:
            if colorId not in output_data:  # 將每個 colorId 的資料儲存
                output_data[colorId] = {
                    "seasonName": "X",  # 這裡假設 seasonName 是 'X'
                    "clothes": []
                }

        output_data[colorId]["clothes"].append({
            "clothingId": clothingId,
            "imageUrl": imageUrl,
            "UniqloUrl": UniqloUrl,
            "category": clothes_category
        })

# 根據 colorId 中的數字部分進行排序
sorted_output_data = dict(sorted(output_data.items(), key=lambda x: int(x[0][3:])))

# 將結果寫入 JSON 檔案
output_file = "uniqlo_clothing_data.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(sorted_output_data, f, ensure_ascii=False, indent=4)

print(f"資料已儲存到 {output_file}")

# # 建立Request物件，附上Request Headers與Request Data。
# # Request Data：發送請求包含的附加資訊Request Payload(veiw source點開後複製)
# request_data = {"url":"/tw/zh_TW/c/all_women-tops.html","pageInfo":{"page":1,"pageSize":24},"belongTo":"pc","rank":"overall","priceRange":{"low":0,"high":0},"color":[],"size":[],"identity":[],"exist":[],"categoryCode":"all_women-tops","searchFlag":False,"description":"","stockFilter":"warehouse"}
# request = req.Request(women_clothes_url, headers = {
#                         "Content-type":"application/json",  # API請求的資料格式
#                         "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
#                     }, data = json.dumps(request_data).encode("utf-8") # Request Payload為json，須轉成字串且使用utf-8編碼
#                     )

# # 發出請求，將結果讀出且以utf-8解碼
# with req.urlopen(request) as response:
#     result = response.read().decode("utf-8")

# # 解析json格式的資料，取得想要的內容
# result = json.loads(result)  #把讀到的json字串(result)轉換成字典dict後回傳進result

# # 從字典中取出資料
# items = result["resp"][0]["productList"]
 
# for item in items:
#     clothingId = item["code"]  

#     colorId = item["colorNums"]  # UQ顏色編號：如COL01
#     colorPic = item["colorPic"]  
#     imageUrl = [f"https://www.uniqlo.com/tw{COL}" for COL in colorPic]
    
#     chipPic = item["chipPic"]  
#     color_block_url = [f"https://www.uniqlo.com/tw{CHIP}" for CHIP in chipPic]

#     clothes_category = []  
#     for product in item["categoryCode"]:  
#         if product == "all_women-tops":
#             clothes_category.append(product)

#     productCode = item["productCode"]  # UQ商品代號：如u0000000050507
#     UniqloUrl = f"https://www.uniqlo.com/tw/zh_TW/product-detail.html?productCode={productCode}"

#     print(f"{clothingId}")
#     print(imageUrl)
#     print(f"{colorId}")
#     print(color_block_url)
#     print(f"{clothes_category}")
#     print(UniqloUrl)
#     print("-" * 40)

# # 結果整理：
# clothes_data = {}
# output_data = {"clothes": []}
# for cid, info in clothing_data.items():
#     output_data["clothes"].append({
#         "clothingId": cid,
#         "colorId": sorted(list(info["colorIdSet"])),
#         "seasonName": "X",  # 這裡先寫死 "X"，你也可以自行增加邏輯
#         "blockUrl": info["blockUrls"],
#         "imageUrl": info["imageUrls"],
#         "uniqloUrl": info["uniqloUrl"]
#     })

# json_file_path = os.path.join(local_path, "uniqlo_data.json")
# with open(json_file_path, "w", encoding="utf-8") as f:
#     json.dump(output_data, f, ensure_ascii=False, indent=4)

# print(f"數據已儲存至 JSON 檔：{json_file_path}")





# print(result["resp"][0]["productList"][0]["colorPic"])
# local_path = r"C:\Users\TMP214\Desktop\Topics\UNIQLO"
# os.makedirs(local_path, exist_ok=True)
# print(f"圖片儲存路徑：{local_path}")

# # 用於存放爬取的商品資訊
# clothing_data = {}