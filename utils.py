from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import requests
from tqdm import tqdm
import re
from lxml import etree

def getEmail(homeLink):
    response=requests.get(homeLink)
    text=response.text
    patterns=[
    "[A-Za-z0-9\s]+@[A-Z0-9a-z\s]+.[A-Za-z\s]{2,}",
    "[A-Za-z0-9\s]+\[at\][A-Z0-9a-z\s]+\[dot\][A-Za-z\s]{2,}",
    "[A-Za-z0-9\s]+\(at\)[A-Z0-9a-z\s]+\(dot\)[A-Za-z\s]{2,}",
    "[A-Za-z0-9\s]+at[A-Z0-9a-z\s]+dot[A-Za-z\s]{2,}",]
    return [re.findall(pattern,text)for pattern in patterns]

def homepage2email(hrefs):
    emails=[]
    for href in tqdm(hrefs):
        try:
            emails.append(getEmail(href))
        except Exception as e:
            print(href+' : '+str(e))
            emails.append([])
    return emails

def crawlPage(userChoices, base_url):
    url = base_url + userChoices
    driver = webdriver.Chrome()
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'table')))
    page = etree.HTML(driver.page_source)
    trs = page.xpath('//*[@id="ranking"]/tbody/tr')
    driver.close()

    print('Successfully get the page!')
    print(trs)

    return trs

def getUInfo(Utr):
    tds=Utr.xpath('td/text()')
    return '@'.join(tds)

def getUProfsInfos(Uprofs):
    profs=Uprofs.xpath('td/div/div/table/tbody/tr')
    profs=profs[::2] # skip noisy tr
    profsInfos=[prof.xpath('td')for prof in profs] #[professors,infos]  e.g. 30*4
    return [getProfInfos(profInfos) for profInfos in profsInfos]

def getProfInfos(profInfos):
    personal=profInfos[1]
    pubs=profInfos[2].xpath('small/a/text()')[0]
    adjs=profInfos[3].xpath('small/text()')[0]
    Pname=personal.xpath('small/a[1]/text()')[0]
    homepageLink=personal.xpath('small/a[1]/@href')[0]
    return [Pname,homepageLink,pubs,adjs]