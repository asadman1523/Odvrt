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
    formatStr = ""
    defaultFormat = "%code %title %actor"

    def __init__(self, list, download, formatStr):
        super().__init__()
        self.fileList = list
        self.downloadThumbnail = download
        self.formatStr = formatStr

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

                            # Full name
                            fullTitle = soup.find('h1').text.split('\n')

                            # code & title
                            title = ""
                            code = ""
                            fillCode = False
                            fillTitle = False
                            for i in range(len(fullTitle)):
                                if not fillCode and fullTitle[i] != '':
                                    code = fullTitle[i]
                                    fillCode = True
                                elif not fillTitle and fullTitle[i] != '':
                                    title = fullTitle[i]
                                    break

                            # thumbnail
                            thumbnail = soup.find('img')

                            # actors
                            actorsObj = soup.findAll('h6', class_="card-title")
                            actors = []
                            for actor in actorsObj:
                                tmpStr = actor.text.strip().replace('\n', '')
                                actors.append(tmpStr)

                            # Some title may have actors name, remove it
                            for actor in actors:
                                print(actor in title)
                                title = title.replace(actor, '')
                            title = title.replace('\n', ' ').strip()

                            # Fill fields
                            fullName = self.formatStr
                            if fullName == "":
                                fullName = self.defaultFormat

                            if '%code' in fullName:
                                fullName = fullName.replace('%code', code)
                            if '%title' in fullName:
                                fullName = fullName.replace('%title', title)
                            if '%actor' in fullName:
                                fullName = fullName.replace('%actor', " ".join(actors))

                            p = pathlib.Path(file)
                            if p.is_file():
                                p.rename(p.with_stem(fullName))
                                # print(p.with_stem(afterFormat))
                                if self.downloadThumbnail:
                                    # print(thumbnail['src'])
                                    self.processDownloadImg(thumbnail['src'], str(p.with_name(fullName)))
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