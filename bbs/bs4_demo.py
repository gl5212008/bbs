"""
bs4模块简单示例
"""

from bs4 import BeautifulSoup

with open("xx.html", "r", encoding="utf8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")
    # print(soup.a)
    # print(soup.a["class"])

    # print(soup.select("script"))
    # for i in soup.select("script"):
    #     i.decompose()  # 删除

    # 查看html的text
    # print(soup.text)  # 只保留文本内容
    print(soup.prettify())