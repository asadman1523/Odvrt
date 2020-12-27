import requests
import sys
import re
import pathlib
import shutil
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter


# 取得副檔名
def getExtension(url):
    suffix = re.findall("\.\w+$", url)
    if len(suffix) > 0:
        suffix = suffix[0]
        return suffix


# 下載圖片
def processDownloadImg(url, dst):
    suffix = getExtension(url)

    r = getResponse(url, True)
    if r.status_code == 200:
        with open(dst + suffix, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)


def rename(fileList, downloadThumbnail):
    if len(fileList) == 0:
        # print('No file detect')
        return

    # Get all files name together and catch number only
    try:
        i = 0
        while i < len(fileList):
            file = fileList[i]
            code = re.findall("([A-Z]+-\d+)", file)

            # Get data
            if len(code) == 1:
                resp = requests.get('https://www.libredmm.com/movies/' + code[0])
                resp = getResponse('https://www.libredmm.com/movies/' + code[0], )
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    result = soup.find('h1').text
                    thumbnail = soup.find('img')
                    afterFormat = result.strip().replace('\n', ' ')
                    # print(afterFormat)
                    p = pathlib.Path(file)
                    if p.is_file():
                        p.rename(p.with_stem(afterFormat))
                        # print(p.with_stem(afterFormat))
                        if downloadThumbnail:
                            # print(thumbnail['src'])
                            processDownloadImg(thumbnail['src'], str(p.with_name(afterFormat)))

            else:
                print("Cannot find any video code:" + file)
            i = i + 1
    except:
        # print("Unexpected error:" 。sys.exc_info()[0])
        raise


def getResponse(url, isStream=False):
    req = requests.session()
    req.mount('http://', HTTPAdapter(max_retries=5))
    req.mount('https://', HTTPAdapter(max_retries=5))
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    response = req.get(url, headers=headers, stream=isStream, timeout=5)
    response.encoding = 'utf-8'
    return response


class RenameFunc:
    pass
