"""
Original author: 功夫熊猫学python
Lunk: https://blog.csdn.net/spiderwower/article/details/136608172

Improver: OddMiss
Github: https://github.com/OddMiss

v2 (2025.01.03)

- Use Edge browser to save webpage as PDF
- Add a function to convert PDF to text, which can detect if the web is blocked and the Internet status

Attention: some pictures in the webpage may not be saved in the PDF file, so you need to check the PDF file manually.
"""

import os
import json
from datetime import datetime
from time import sleep
from PyPDF2 import PdfReader

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

Link_Path = "D:/AI_data_analysis/BeijingChaoJia-Data/All_Articles_Link/"
Content_Path = "D:/AI_data_analysis/BeijingChaoJia-Data/All_Articles_Content/"
Content_Path_Windows = Content_Path.replace("/", "\\")

def Json_Dict(Json_Path):
    """
    Json_Path: Path of a json file
    """
    with open(Json_Path, 'r', encoding='utf-8') as file:
        data_dict = json.load(file)  # Read and convert JSON to a dictionary
    return data_dict

def Dict_To_Json(Dict, Json_Path):
    """
    Dict: any dict format variable in python

    Json_Path: Path of a json file
    """
    with open(Json_Path, 'w', encoding='utf-8') as file:
        json.dump(Dict, file, ensure_ascii=False, indent=4)  # Write as formatted JSON

def PDF2Text(pdf_path, actual_page_list=[], ALL_PAGES=False):
    # print("PDF file:", pdf_path)
    if ALL_PAGES:
        page_list = list(range(len(PdfReader(pdf_path).pages)))
    else:
        page_list = [num - 1 for num in actual_page_list]
    text = ""
    with open(pdf_path, 'rb') as f:
        PDF = PdfReader(f)
        # print(f"PDF page(s) num: {len(PDF.pages)}" + "\n")
        for page_num in page_list:
            text = (
                text 
                + "*" * 80
                + "\n"
                + f"{page_num + 1} page of PDF" 
                + "\n\n"
                + PDF.pages[page_num].extract_text().replace(" ", "")
                + "\n"
            )
    # print(text)
    return text

def scroll_to_load_images(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)  # Wait for new content to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

if __name__ == "__main__":

    Begin_Date = "20210721"
    Change_Date = input(f"Begin Date: {Begin_Date}, would you like to change it? (y/n) ")
    if Change_Date == "y":
        Begin_Date = input("Please enter the new begin date (e.g. 20191219): ")
        if len(Begin_Date) != 8 or not Begin_Date.isdigit():
            print("The date format is incorrect! Please enter the date again.")
            exit()

    options = Options()
    settings = {
        "recentDestinations": [{
            "id": "Save as PDF",
            "origin": "local",
            "account": ""
        }],
        "selectedDestinationId": "Save as PDF",
        "version": 2,  # 另存为pdf，1 是默认打印机
        "isHeaderFooterEnabled": False,  # 是否勾选页眉和页脚
        "isCssBackgroundEnabled": True,  # 是否勾选背景图形
        "mediaSize": {
            "height_microns": 297000,
            "name": "ISO_A4",
            "width_microns": 210000,
            "custom_display_name": "A4",
        },
    }
    prefs = {
        'printing.print_preview_sticky_settings.appState': json.dumps(settings),
        'savefile.default_directory': Content_Path_Windows, 
        # Note: The directory link must be in Windows format (e.g. "D:\\AI_data_analysis\\") 
    }

    # options.add_argument("--headless")  # Run without GUI
    options.add_argument('--enable-print-browser') # 这一行试了，可用可不用
    options.add_argument('--kiosk-printing')  # 静默打印，无需用户点击打印页面的确定按钮
    options.add_experimental_option('prefs', prefs)
    service = Service(executable_path="D:/edgedriver_win64/msedgedriver.exe") # Edge浏览器驱动路径
    driver = webdriver.Edge(service=service, options=options)

    for filename in os.listdir(Link_Path):
        Json_Path = Link_Path + filename
        Article_Dict = Json_Dict(Json_Path)
        for Date in Article_Dict.keys():
            Article_List = Article_Dict[Date]
            Article_Title = Article_List[0].replace("\n", "")
            Article_Url = Article_List[1]
            Format_Date = datetime.strptime(Date, "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d")
            # Find the weekday (1=Monday, 7=Sunday)
            weekday = datetime.strptime(Date, "%Y-%m-%d %H:%M:%S").weekday() + 1
            File_Name = f"{Format_Date}-{weekday}.pdf"
            if Format_Date >= Begin_Date:
                if not os.path.exists(Content_Path + File_Name):
                    print("*" * 60)
                    print(f"{Format_Date} Link:", Article_Url)

                    driver.get(Article_Url)

                    sleep(3)

                    # Scroll down to load all images
                    scroll_to_load_images(driver)

                    # 1.自定义pdf文件名字
                    driver.execute_script(f'document.title="{File_Name}";')

                    sleep(3)

                    driver.execute_script('window.print();')

                    sleep(4)

                    # 2.默认pdf文件名字
                    # driver.execute_script('window.print();')

                    # sleep这一行非常关键，时间短了，导致pdf还未生成，浏览器就关闭了。
                    # 如果html图片较多，保存的pdf文件较大，或者如果电脑配置不好，等待时间可以再设置长一点。

                    text = PDF2Text(Content_Path + File_Name, ALL_PAGES=True)
                    if "ERR_INTERNET_DISCONNECTED" in text:
                        print("Internet disconnected! Please check the network connection.")
                        os.remove(Content_Path + File_Name)
                        break
                    elif "访问过于频繁，请用微信扫描二维码进行访问" in text:
                        print("The web is blocked by the server! Please try again later.")
                        os.remove(Content_Path + File_Name)
                        break
                    print(f"Saved PDF: {Content_Path + File_Name}")
                
            # elif os.path.exists(Content_Path + File_Name):
            #     print("*" * 60)
            #     print(f"{Format_Date} Link:", Article_Url)
            #     print(f"PDF file {Content_Path + File_Name} already exists!")
    driver.quit()  # Ensure the driver is closed after processing
