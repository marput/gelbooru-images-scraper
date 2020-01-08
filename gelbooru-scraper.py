import requests
import time
import shutil
import errno
import urllib.request
import os
import sys
import tempfile
import re
import lxml
import logging
from datetime import datetime
from bs4 import BeautifulSoup

downloadAll = False

def is_pathname_valid(pathname: str) -> bool:
    '''
    `True` if the passed pathname is a valid pathname for the current OS;
    `False` otherwise.
    '''
    try:
        if not isinstance(pathname, str) or not pathname:
            return False

        _, pathname = os.path.splitdrive(pathname)

        root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
            if sys.platform == 'win32' else os.path.sep
        assert os.path.isdir(root_dirname)   # ...Murphy and her ironclad Law

        root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep

        for pathname_part in pathname.split(os.path.sep):
            try:
                os.lstat(root_dirname + pathname_part)
            except OSError as exc:
                if hasattr(exc, 'winerror'):
                    if exc.winerror == ERROR_INVALID_NAME:
                        return False
                elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                    return False
    except TypeError as exc:
        return False
    else:
        return True

def getPID(url):
    pid = 0
    expression = '\d+(\.\d+)?$'
    temp = re.search(expression, str(url))
    if temp is None:
        pid = 0 
        return pid
    else:
        pid = int(temp.group(0))
        return pid
     
def getPage(pid):
    page = 1
    if pid is None:
        return int(page)
    else:
        return int(pid/42+1)

def getPIDFromPage(page):
    if int(page) == 1:
        return 0
    else:
        return int(page)*42+42
  
def advancePage(url):
    pid = getPID(url)
    pid = int(pid+42)
    expression = '\d+(\.\d+)?$'
    address = re.sub(expression, str(pid), url)
    return address

def getPages(navigatorInnerText):
    listOfSitePages = []
    for i in range(0, len(navigatorInnerText)):
        try:
            listOfSitePages.append(int(navigatorInnerText[i].text))
        except TypeError:
            continue
        except ValueError:
            continue
    return listOfSitePages


def getHighestPage(listOfSitePages, listOfHrefs, highPage):
    highestPage = 1
    for nigger in listOfHrefs:
        if int(getPage(getPID(nigger))) > highestPage:
            highestPage = int(getPage(getPID(nigger)))
    for nigger in listOfSitePages:
        if highestPage < int(nigger):
            highestPage = int(nigger)
        if highestPage < int(highPage):
            highestPage = int(highPage)
    return highestPage

def getListOfHrefs(pagination):
    siteHrefs = pagination.findAll('a')
    listOfHrefs = []
    for nigger in siteHrefs:
        listOfHrefs.append(nigger.get('href'))
    return listOfHrefs    

def getAddress():
    while(True):
        print("Enter the URL address you want to scrape on Gelbooru: ")
        address = input()
        try:
            addressRequest = requests.head(address);
            print(addressRequest.status_code)
        except requests.ConnectionError:
            print("Failed to connect.")
            print("Request returned with status code " + str(addressRequest.status_code))
            continue
        except:
            print("Unknown error. (Are you sure you've entered the address correctly?)")
            continue
        testExpression = '^https:\/\/gelbooru\.com.+|^http:\/\/gelbooru\.com.+|^www\.gelbooru\.com.+|^https:\/\/www\.gelbooru\.com.+|^http:\/\/www\.gelbooru\.com.+'
        searchObj = re.search(testExpression, address)
        if 100 <= addressRequest.status_code <= 299 and searchObj:
            return address

def getPath():
    while(True):
        print("Enter the path to directory where images will get saved to (Maximum 150 characters): ")
        path = input()
        if is_pathname_valid(path) and len(path) < 150:
            return path

tokens = (
  ('DIGIT', re.compile(r"(?<!\.)\b[0-9]+\b(?!\.)")),
  ('RANGE', re.compile('-')),
  ('TERMINATOR', re.compile(';')),
  ('STRING', re.compile('.')), 
)

def tokenizer(s):
    i = 0
    lexeme = []
    while i < len(s):
        match = False
        for token, regex in tokens:
            result = regex.match(s, i)
            if result:
                lexeme.append((token, result.group(0)))
                i = result.end()
                match = True
                break
        if not match:
            raise Exception('lexical error at {0}'.format(i))
    return lexeme

def getUserInput(message):
    userInput = input(message)
    return userInput

def cleanUserInput(uncleanTokens):
    cleanTokens = []
    value = ""
    for i in range(0, len(uncleanTokens)):
        if uncleanTokens[i][0] != 'STRING':
            value = uncleanTokens[i][1]
            if uncleanTokens[i][0] == 'DIGIT':
                if uncleanTokens[i][1] == '0':
                    global downloadAll
                    downloadAll = True
                    break
                else:
                    value = int(value.lstrip('0'))
            cleanTokens.append((uncleanTokens[i][0], value))
    return cleanTokens

def checkRangeCondition(cleanTokens, i):
    if cleanTokens[i-1][0] == 'DIGIT' and cleanTokens[i+1][0] == 'DIGIT':
        return True
    else:
        return False

def parseUserInput(cleanTokens):
    listOfPages = []
    for i in range(0, len(cleanTokens)):
        if cleanTokens[i][0] == 'DIGIT':
            listOfPages.append(cleanTokens[i][1])
        elif cleanTokens[i][0] == 'RANGE':
            if checkRangeCondition(cleanTokens, i):
                listOfPages.pop()
                start = cleanTokens[i-1][1]
                end = cleanTokens[i+1][1]
                if start < end:
                    listOfPages.extend(range(start, end))
                    listOfPages.append(end)
                elif end < start:
                    listOfPages.extend(range(end, start))
                    listOfPages.append(start)
                elif start == end:
                    listOfPages.append(end)

        elif cleanTokens[i][0] == 'TERMINATOR':
            return listOfPages
    return listOfPages

def makePreviewLinks(soup):
    tempPreviewLinks = []
    previewLinks = []
    expression = '\/thumbnails\/'
    for img in soup.findAll('img'):
        tempPreviewLinks.append(img.get('src'))
    for nigger in tempPreviewLinks:
        searchObj = re.search(expression, str(nigger))
        if searchObj:
            previewLinks.append(nigger)
    return previewLinks

def makeImageLinks(previewLinks):
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
    return listOfImages

def getDownloadLink(listOfImages):
    finalLinks = []
    for i in range(0, len(listOfImages)):
        finalLink = listOfImages[i]
        isError = False
        try:
            time.sleep(0.5)
            urllib.request.urlopen(finalLink)
        except urllib.error.HTTPError as e:
            logging.error("PNG link returned with HTTP code " + str(e.code) + " " + finalLink)
            print("Falling back to JPG")
            finalLink = re.sub('.png', '.jpg', finalLink)
            isError = True
        except urllib.error.URLError as e:
            logging.error("PNG URL error: " + str(e.reason) + " " + finalLink)
            print("Falling back to JPG")
            finalLink = re.sub('.png', '.jpg', finalLink)
            isError = True
        if isError:
            try:
                time.sleep(0.5)
                urllib.request.urlopen(finalLink)
                isError = False
            except urllib.error.HTTPError as e:
                logging.error("JPG link returned with code " + str(e.code) + " " + finalLink)
                print("Falling back to JPEG")
                finalLink = re.sub('.jpg', '.jpeg', finalLink)
            except urllib.error.URLError as e:
                logging.error("JPG URL error: " + str(e.reason) + " " + finalLink)
                print("Falling back to JPEG")
                finalLink = re.sub('.jpg', '.jpeg', finalLink)
        if isError:
            try:
                time.sleep(0.5)
                urllib.request.urlopen(finalLink)
                isError = False
            except urllib.error.HTTPError as e:
                logging.error("Final iteration JPEG link returned with code " + str(e.code))
                print("Final iteration returned with HTTP error code, check log file for details")
            except urllib.error.URLError as e:
                logging.error("Final iteration JPEG URL error: " + str(e.reason))
                print("Final iteration returned with URL error, check log file for details")
        finalLinks.append(finalLink)
    return finalLinks

def downloadImage(finalLinks, imageTitles):
    for i in range(0, len(finalLinks)):
        try:
            filename = str(imageTitles[i][:150])
            fullFileName = os.path.join(str(path), filename)
            fullFileName = str(fullFileName)
        except IndexError:
            filename = str(int(time.time()))
            fullFileName = os.path.join(str(path), filename)
            fullFileName = str(fullFileName)
        try:
            urllib.request.urlretrieve(finalLinks[i], fullFileName)
        except urllib.error.HTTPError as e:
            logging.error("Failed to download image (HTTP Error) with code: " + e.code + ". From URL: " + str(finalLinks[i]) + ". Is the URL valid?")
        except urllib.error.URLError as e:
            logging.error("Failed to download image (URL Error) with reason: " + str(e.reason) + ". From URL: " + str(finalLinks[i]) + ". Is the URL valid?")
    


def getImageTitles(soup):
    tempImageTitles = []
    imageTitles = []
    expression = 'rating:'
    for img in soup.findAll('img'):
        tempImageTitles.append(img.get('title'))
    for nigger in tempImageTitles:
        searchObj = re.search(expression, str(nigger))
        if searchObj:
            nigger = re.sub('\/', '', nigger)
            imageTitles.append(nigger)
    return imageTitles

def checkValidPages(listOfPages, lastPage):
    for i in range(0, len(listOfPages)):
        if int(listOfPages[i]) not in range(1, int(lastPage+1)):
            del listOfPages[i]
            i-=1
    return listOfPages

def checkIfPageRange(listOfPages):
    if len(listOfPages) > 0:
        return True
    else:
        return False

def replacePID(url, pid):
    expression = '\d+(\.\d+)?$'
    address = re.sub(expression, str(pid), str(url))
    return address

opener=urllib.request.build_opener()
opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
urllib.request.install_opener(opener)

logging.basicConfig( filename="gelbooru-image-scraper.log",
                     filemode='w',
                     format ='%(asctime)s - %(levelname)s - %(message)s', )

url = getAddress()
path = getPath()

page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')
pagination = soup.find("div", class_="pagination")
pages = pagination.findAll('a')
currentPage = pagination.find('b').text
listOfSitePages = getPages(pages)
listOfHrefs = getListOfHrefs(pagination)
lastPage = getHighestPage(listOfSitePages, listOfHrefs, int(currentPage))

while(True):
    userInput = getUserInput("Enter pages/page ranges to download images from, separated by commas.\n Input 0 to download from eevery page. \n Ranges are inclusive, written like 25-30 (pages from 25 to 30).\n")
    tempArray = userInput.split(",")
    userInputArray = []
    for i in range(0, len(tempArray)):
        userInputArray.append(tempArray[i].strip())
        uncleanTokens = []
        for i in range(0, len(userInputArray)):
            text = userInputArray[i].strip()
            results = tokenizer(text)
            for j in range(0, len(results)):
                uncleanTokens.append((results[j][0], results[j][1]))
        cleanTokens = cleanUserInput(uncleanTokens)
        listOfPages = parseUserInput(cleanTokens)
        listOfPages = list(set(listOfPages))
        listOfPages = checkValidPages(listOfPages, lastPage)
    if checkIfPageRange(listOfPages):
        break

if downloadAll == True:
    listOfPages = []
    listOfPages.extend(0, int(lastPage))
    listOfPages.append(int(lastPage))

for i in range(0, len(listOfPages)):
    pid = getPIDFromPage(listOfPages[i])
    url = replacePID(url, pid)
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    pagination = soup.find("div", class_="pagination")
    pages = pagination.findAll('a')
    pid = getPID(url)
    currentPage = pagination.find('b').text
    listOfSitePages = getPages(pages)
    lastPage = getHighestPage(listOfSitePages, listOfHrefs, int(currentPage))
    imageTitles = getImageTitles(soup)
    previewLinks = makePreviewLinks(soup)

    listOfSitePages = getPages(pages)

    listOfImages = makeImageLinks(previewLinks)
    listOfImages = getDownloadLink(listOfImages)
    print("Downloading page " + str(i+1) + " out of " + str(len(listOfPages)))
    print("Currently on page " + str(currentPage) + " out of " + str(lastPage) + " in total.")
    downloadImage(listOfImages, imageTitles)

