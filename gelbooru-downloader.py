import requests
import time
import shutil
import os
import sys
import re
import logging
import readline, glob
from datetime import datetime
from bs4 import BeautifulSoup

log_file_name = "gelbooru-downloader.log"

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '#', printEnd = "\r\n"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

def completePath(text, state):
    return (glob.glob(text+'*' + '/')+[None])[state]

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
        return int(page-1)*42
  
def advancePage(url):
    pid = getPID(url)
    if int(pid) == 0:
        pid = 42
    else:
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
        address = input("Enter the URL address you want to scrape on Gelbooru: ")
        try:
            addressRequest = requests.head(address)
            print(addressRequest.status_code)
        except requests.ConnectionError:
            print("Failed to connect.")
            print("Request returned with status code " + str(addressRequest.status_code))
            continue
        except:
            print("Unknown error. (Are you sure you've entered the address correctly?)")
            continue
        testExpression = '.*gelbooru\.com.+'
        searchObj = re.search(testExpression, address)
        if 100 <= addressRequest.status_code <= 299 and searchObj:
            return address

def getPath():
    while True:
        readline.set_completer_delims(' \t\n;')
        readline.parse_and_bind("tab: complete")
        readline.set_completer(completePath)
        path = input("Enter the path to directory where images will get saved to: ")
        path = os.path.expanduser(path)
        if os.path.isdir(path): 
            return path
        print("Path doesn't exist, try again.")

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

extensions = (
    ('.png', r".png"),
    ('.jpg', r".jpeg"),
    ('.jpg', r".jpg"),
    ('.gif', r".gif"),
    ('.webm', r".webm"),
    ('.mp4', r".mp4")
)

def getDownloadLink(listOfImages, session):
    finalLinks = []
    printProgressBar(0, len(listOfImages), 'Making links...', 'Complete', length=50)
    for i in range(0, len(listOfImages)):
        finalLink = listOfImages[i]
        for j in range(1, len(extensions)):
            try:
                r = requests.head(finalLink)
                r.raise_for_status()
            except requests.exceptions.HTTPError as errh:
                finalLink = re.sub(extensions[j-1][1], extensions[j][1], finalLink)
                continue
            except requests.exceptions.ConnectionError as errc:
                with open(log_file_name, 'a') as log_file:
                    log_file.write(strftime("%d-%m-%Y %H:%M:%S", localtime()) + " Connection error:",errc + '\n')
                break
            except requests.exceptions.Timeout as errt:
                with open(log_file_name, 'a') as log_file:
                    log_file.write(strftime("%d-%m-%Y %H:%M:%S", localtime()) + " Timeout error:",errt + '\n')
                break
            except requests.exceptions.TooManyRedirects as errr:
                with open(log_file_name, 'a') as log_file:
                    log_file.write(strftime("%d-%m-%Y %H:%M:%S", localtime()) + " Redirects error:",errr + '\n')
                break
            except requests.exceptions.RequestException as erre:
                with open(log_file_name, 'a') as log_file:
                    log_file.write(strftime("%d-%m-%Y %H:%M:%S", localtime()) + " Request error:",erre + '\n')
                break
        finalLinks.append(finalLink)
        time.sleep(0.1)
        printProgressBar(i+1, len(listOfImages), 'Making links...', 'Complete', length=50)
    return finalLinks

def determineExtension(link):
    extension = ""
    for element in extensions:
        if re.search(element[1], link):
            extension = element[0]
            return extension
    return "-1"

def downloadPage(finalLinks, session):
    printProgressBar(0, len(finalLinks), 'Downloading...', 'Complete', length=50)
    for i in range(0, len(finalLinks)):
        extension = determineExtension(finalLinks[i])
        if extension == "-1":
            with open(log_file_name, 'a') as log_file:
                log_file.write(strftime("%d-%m-%Y %H:%M:%S", localtime()) + " Unknown extension for link:" + finalLinks[i] + '\n')
            continue
        filename = str(int(time.time())) + extension
        full_path = os.path.join(str(path), filename)
        try:
            r = session.get(finalLinks[i], stream=True)
            r.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            with open(log_file_name, 'a') as log_file:
                log_file.write(strftime("%d-%m-%Y %H:%M:%S", localtime()) + " Http error:",errh + '\n')
            continue
        except requests.exceptions.ConnectionError as errc:
            with open(log_file_name, 'a') as log_file:
                log_file.write(strftime("%d-%m-%Y %H:%M:%S", localtime()) + " Connection error:",errc + '\n')
            continue
        except requests.exceptions.Timeout as errt:
            with open(log_file_name, 'a') as log_file:
                log_file.write(strftime("%d-%m-%Y %H:%M:%S", localtime()) + " Timeout error:",errt + '\n')
            continue
        except requests.exceptions.TooManyRedirects as errr:
            with open(log_file_name, 'a') as log_file:
                log_file.write(strftime("%d-%m-%Y %H:%M:%S", localtime()) + " Redirects error:",errr + '\n')
            continue
        except requests.exceptions.RequestException as erre:
            with open(log_file_name, 'a') as log_file:
                log_file.write(strftime("%d-%m-%Y %H:%M:%S", localtime()) + " Request error:",erre + '\n')
            continue
        with open(full_path, 'wb') as out_file:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, out_file)
        del r
        time.sleep(0.5)
        printProgressBar(i+1, len(finalLinks), 'Downloading...', 'Complete', length=50)

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
    i = 0
    while 0 <= i < len(listOfPages):
        if not 1 <= int(listOfPages[i]) < lastPage+1:
            del listOfPages[i]
            i-=1
        i+=1
    return listOfPages

def checkIfPageRange(listOfPages):
    if len(listOfPages) > 0:
        return True
    else:
        return False

def replacePID(url, pid):
    expression = '&pid=\d+$'
    properPid = "&pid=" + str(pid)
    searchObj = re.search(expression, url)
    if searchObj:
        address = re.sub(expression, properPid, str(url))
    else:
        address = url + properPid
    return address

def getUncleanTokens(userInput):
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
    return uncleanTokens

def getUserPages(lastPage):
    while(True):
        uncleanTokens = getUncleanTokens(input("Enter pages to scrap images from. Separate inputs by commas, terminate with semicolon. Indicate range with -. Eg. 1-18, 25, 30-35;. There are " + str(lastPage) + " pages in total.\n"))
        cleanTokens = cleanUserInput(uncleanTokens)
        listOfPages = parseUserInput(cleanTokens)
        listOfPages = list(set(listOfPages))
        listOfPages = checkValidPages(listOfPages, lastPage)
        if checkIfPageRange(listOfPages):
            return listOfPages

def downloadPages(session, url, listOfPages):
    for i in range(0, len(listOfPages)):
        pid = getPIDFromPage(int(listOfPages[i]))
        url = replacePID(url, pid)
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        pagination = soup.find("div", class_="pagination")
        pages = pagination.findAll('a')
        pid = getPID(url)
        currentPage = pagination.find('b').text
        listOfSitePages = getPages(pages)
        lastPage = getHighestPage(listOfSitePages, listOfHrefs, int(currentPage))
        previewLinks = makePreviewLinks(soup)
        listOfImages = makeImageLinks(previewLinks)
        listOfImages = getDownloadLink(listOfImages, session)
        print("Downloading page " + str(i+1) + " out of " + str(len(listOfPages)))
        print("Currently on page " + str(currentPage) + " out of " + str(lastPage) + " in total.")
        print(url)
        downloadPage(listOfImages, session)

session = requests.session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'})

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
listOfPages = getUserPages(lastPage)
downloadPages(session, url, listOfPages)


