import requests
import sys
import re
import pathlib
import shutil

from PyQt5.QtCore import QThread, pyqtSignal
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter


class RenameTool(QThread):
    stopProc = False
    countChanged = pyqtSignal(int)
    fileList = []
    downloadThumbnail = False  # Should download img

    def __init__(self, list, download):
        super().__init__()
        self.fileList = list
        self.downloadThumbnail = download

    # 取得副檔名
    def getExtension(self, url):
        suffix = re.findall("\.\w+$", url)
        if len(suffix) > 0:
            suffix = suffix[0]
            return suffix

    # 下載圖片
    def processDownloadImg(self, url, dst):
        suffix = self.getExtension(url)

        r = self.getResponse(url)
        if r.status_code == 200:
            with open(dst + suffix, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)

    def run(self):
        try:
            self.countChanged.emit(0)
            if len(self.fileList) == 0:
                print('No file detect')
                return

            # Get all files name together and catch number only

            codeSet = []
            i = 0
            while i < len(self.fileList) and not self.stopProc:
                print("Resolving..." + self.fileList[i])
                prog = i / len(self.fileList) * 100
                self.countChanged.emit(prog)
                file = self.fileList[i]
                reResult = re.findall("(\w+-\d+)", file)
                if len(reResult) == 0:
                    reResult = re.findall("([a-zA-Z]+)(\d+)", file)
                    if len(reResult) == 0:
                        print("Code not found")
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
                        resp = self.getResponse('https://www.libredmm.com/movies/' + code)
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
                                if self.downloadThumbnail:
                                    # print(thumbnail['src'])
                                    self.processDownloadImg(thumbnail['src'], str(p.with_name(afterFormat)))
                            break
                        else:
                            raise
                    except:
                        print("Unexpected error:" + str(sys.exc_info()))
                        print(code + " Download failed")
                        pass
                i = i + 1
            self.countChanged.emit(101)
        except:
            print("Unexpected error:" + str(sys.exc_info()))
            raise

    def getResponse(self, url, stream=False):
        req = requests.session()
        req.mount('http://', HTTPAdapter(max_retries=5))
        req.mount('https://', HTTPAdapter(max_retries=5))
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        response = req.get(url, headers=headers, stream=stream, timeout=5)
        response.encoding = 'utf-8'
        return response
