import time
import sys
import os

import pyperclip

import requests
import json

def getNameAndType(clipboard):
    #TODO POE 클라에서 복사된 것인지 좀 더 나은 방법으로 검사
    if clipboard.startswith('희귀도:') == False:
        return None, None
    try:
        #카드 같은 아이템은 이름이 없고 타입만 있다.
        if clipboard.splitlines()[2].startswith('---'):
            return None, clipboard.splitlines()[1]
        else:
            return clipboard.splitlines()[1], clipboard.splitlines()[2]
    except:
        return None

def findTradeInfo(clipboard):
    name, itemtype = getNameAndType(clipboard)
    if itemtype == None:
        return None
    print('finding ' + itemtype)
    headers = {'Content-Type': 'application/json'}
    if name != None:
        payload = {"query":{"status":{"option":"online"},"name": name,"type":itemtype ,"stats":[{"type":"and","filters":[]}]},"filters":{"trade_filters":{"filters":{"indexed":{"option":"1day"}},"disabled":False}},"sort":{"price":"desc"}}
    else:
        payload = {"query":{"status":{"option":"online"},"type":itemtype ,"stats":[{"type":"and","filters":[]}]},"filters":{"trade_filters":{"filters":{"indexed":{"option":"1day"}},"disabled":False}},"sort":{"price":"desc"}}
    url = "https://poe.game.daum.net/api/trade/search/Legion"    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        print( 'post error ' + str(response.status_code))
        return
    
    itemid = response.json()['id']
    list = response.json()['result']
    print( "total:" + str(response.json()['total'] ))
    url='https://poe.game.daum.net/api/trade/fetch/'
    maxCount = 10
    step = int(len(list)/maxCount) + 1
    for i in range(0,len(list),step):
        url = url + list[i] + ','
    url = url[:-1]
    url = url + '?query=' + itemid
    
    result = requests.get(url)
    if result.status_code != 200:
        print( 'get error ' + str(response.status_code))
        return
        
    print( 'itemtype -----' )
    infolist = result.json()['result']
    for info in infolist:
        print(info['listing']['price'])

def mainLoop():
    #TODO clipboard event hook 사용하게 바꿔야 한다.
    print('Press Ctrl+C in POE client')
    pyperclip.copy('')
    recent_value = ''
    while True:
        clipboard = pyperclip.paste()
        if clipboard != recent_value:
            print( 'clipboard changed' )
            recent_value = clipboard
            findTradeInfo(clipboard)
            
        time.sleep(0.1)

if __name__ == "__main__":
    mainLoop()
