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
        codeSet = []
        i = 0
        while i < len(fileList):
            file = fileList[i]
            reResult = re.findall("(\w+-\d+)", file)
            if len(reResult) == 0:
                reResult = re.findall("([a-zA-Z]+)(\d+)", file)
                # 拼接
                for result in reResult:
                    if len(result) > 1:
                        codeSet = codeSet + [result[0] + "-" + result[1]]
            else:
                codeSet.append(reResult[0])
            for code in codeSet:
                try:
                    print("Downloading..." + code)
                    # Get data
                    resp = getResponse('https://www.libredmm.com/movies/' + code, )
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, 'html.parser')
                        # name
                        name = soup.find('h1').text
                        thumbnail = soup.find('img')
                        afterFormat = name.strip().replace('\n', ' ')
                        p = pathlib.Path(file)
                        if p.is_file():
                            p.rename(p.with_stem(afterFormat))
                            # print(p.with_stem(afterFormat))
                            if downloadThumbnail:
                                # print(thumbnail['src'])
                                processDownloadImg(thumbnail['src'], str(p.with_name(afterFormat)))
                        break
                    else:
                        raise
                except:
                    print(code + " Download failed")
                    pass
            i = i + 1
    except:
        # print("Unexpected error:" + sys.exc_info()[0])
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
