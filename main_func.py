import requests
import sys
import re
import os
import pathlib
from bs4 import BeautifulSoup

# We can accept array actually. But for UI update we process one by one.
def rename(fileList):
    if len(fileList) == 0:
        print('No file detect')
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
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    result = soup.find('h1').text
                    afterFormat = result.strip().replace('\n', ' ')
                    #print(afterFormat)
                    p = pathlib.Path(file)
                    if p.is_file():
                        p.rename(p.with_stem(afterFormat))
                        print(p.with_stem(afterFormat))
            else:
                print("Cannot find any video code:" + file)
            i = i + 1
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise


class RenameFunc:
    pass
