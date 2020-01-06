import requests
import time
import shutil
import urllib.request
import os
import re
import lxml
from datetime import datetime
from bs4 import BeautifulSoup
opener=urllib.request.build_opener()
opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
urllib.request.install_opener(opener)
url = 'https://gelbooru.com/index.php?page=post&s=list&tags=asano_fuuka'
page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')
trashInput = soup.findAll("div", class_="thumbnail-preview")
trashInput = soup.findAll("img")
trashInput = soup.findAll(src=True)
temp = []
for img in soup.findAll('img'):
    temp.append(img.get('src'))
previewLinks = []
expres = '\/thumbnails\/'
for i in range(0, len(temp)):
    searchObj = re.search(expres, str(temp[i]))
    if searchObj:
        previewLinks.append(temp[i])
for nigger in previewLinks:
    print(nigger)
firstExpression = 'gelbooru'
secondExpression = 'thumbnails'
thirdExpression = 'thumbnail_'
fourthExpression = '.jpg|.jpeg'
firstReplacement = 'img2.gelbooru'
secondReplacement = 'images'
thirdReplacement = ''
fourthReplacement = '.png'
listOfImages = []
link = ""
for i in range(0, len(previewLinks)):
    link = previewLinks[i]
    link = re.sub(firstExpression, firstReplacement, link)
    link = re.sub(secondExpression, secondReplacement, link)
    link = re.sub(thirdExpression, thirdReplacement, link)
    link = re.sub(fourthExpression, fourthReplacement, link)
    listOfImages.append(link)
for fucker in listOfImages:
    print(fucker)
for i in range(0, len(listOfImages)):
    now = datetime.now()
    timestamp = datetime.timestamp(now)
    finalLink = listOfImages[i]
    isError = False;
    try:
        urllib.request.urlopen(finalLink)
    except urllib.error.HTTPError as e:
        print("JPEG link returned with code " + str(e.code))
        finalLink = re.sub('.png', '.jpg', finalLink)
        isError = True
    except urllib.error.URLError as e:
        print("JPEG URL error: " + str(e.reason))
        finalLink = re.sub('.png', '.jpg', finalLink)
        isError = True
    if(isError):
        try:
            time.sleep(0.5)
            urllib.request.urlopen(finalLink)
        except urllib.error.HTTPError as e:
            print("JPG link returned with code: " + str(e.code))
            finalLink = re.sub('.jpg', '.jpeg', finalLink)
        except urllib.error.URLError as e:
            print("JPG URL Error: " + str(e.reason))
            finalLink = re.sub('.jpeg', '.jpg', finalLink)
    myPath = '/home/cirno/Downloads/papes/'
    filename = str(timestamp)
    fullFileName = os.path.join(myPath, filename)
    fullFileName = str(fullFileName)
    try:
        print(finalLink)
        urllib.request.urlretrieve(finalLink, fullFileName)
    except urllib.error.HTTPError as e:
        print("Final iteration returned with code: " + str(e.code))
    except urllib.error.URLError as e:
        print("URL Error: " + str(e.reason))
    time.sleep(1)

    
