# __author:  Administrator
# date:  2017/2/9
import requests

response = requests.get(
    url='https://i.cnblogs.com/EditDiary.aspx',
    cookies={'.CNBlogsCookie': '128F6D14E7E5608652CF5A9338526A6C9B4B4CFE0BD85EC625DBAFADD93E0CBB8078415C72486FA8366113E622BDD18D873E6AF46238BE38ECB047FDF85DBB490C26E3983E72418FE9FFE2075D47F637347BEFA1'},
    cert='证书文件',
    verify=True
)
print(response.text)
