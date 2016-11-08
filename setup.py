# -*- coding: utf-8 -*-

"""===============================================
Python 3.5
_______________________________________________
DESCRIPTION

xZotHtml:
Given a tag (myTag) the script will enquire Zotero's api and get content for all relevant entities.
The extracted annotations are restructured to better show relationship between markup and notes.
It also allows for tags and images to be assigned.
The function output a list of objects where each object is a markup.

The script will thereafter filter the content according to source and tags.
The different groupings are written to individual files. 

==============================================="""

import xZotHtml as xzh
from bs4 import BeautifulSoup as Soup
from pyzotero import zotero
import json

# load api
"""
apiFile = "/media/sf__x-code/_api/api_zotero_aa.json"
attachDir = 'D://_g_know/_zotero/'
myTag = 'done'
"""
apiFile = "/media/sf__x-code/_api/api_zotero_mm.json"
attachDir = 'D://_k-zotero/' # Unfortunately full path is not always returned with api
myTag = '_test'

with open(apiFile) as data_file:    
    keys = json.load(data_file)
data_file.close()
zot = zotero.Zotero(keys['library_id'], keys['library_type'], keys['api_key'])

"""
GET DATA FROM API AND RESTRUCTURE
"""
db = xzh.ripZotApi(zot,myTag,attachDir)

"""
# save
with open('obj-db_' + str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")) + '.json', 'w') as outfile:
    json.dump(db, outfile, sort_keys = True, indent = 4,
ensure_ascii=False)
"""

"""
WRITE HTML FILES
"""
# html template
dirOut = "data-out/"
outBase = '<html><head><meta><title></title><link rel="stylesheet" type="text/css" href="http://ma3x.com/repo/style-lib.css"></head><body><div id="top"><p></p></div></body></html>'

# hmtl file for every pdf
myList = [(x['src']['srcID'],x['src']['srcBook']) for x in db if (x['src']['srcType']=='zotfile')]
idList = set(myList)
for aID in idList:
    print('looping ' + aID[0] + aID[1])
    outHtml = Soup(outBase,"html.parser")
    filename = aID[1]    
    outHtml.html.head.meta.title.string = filename
    outHtml.html.body.div.p.string = filename
    # Set browser window title 
    refList = [x['item']['content'] for x in db if (x['src']['srcID']==aID[0])]    
    for item in reversed(refList): # reversed() needed since using insert_after below
        outHtml.html.body.div.insert_after(Soup(item,"html.parser"))
    toPrinter = outHtml.prettify("utf-8")
    with open(dirOut + filename + ".html", "wb") as file:
        file.write(toPrinter) 

# html file for every tags. Only first priority
totalTags = []
for item in db:
    if item['item']['level'] == 1:
        totalTags += item['item']['tag']
tagSet = set(totalTags)
for tag in iter(tagSet):        
    print('tag: ' + tag) ## prepare outgoing
    served = False    
    outHtml = Soup(outBase,"html.parser")
    outHtml.html.head.meta.title.string = tag
    outHtml.html.body.div.p.string = tag
    # dbRev = db.reverse()
    for x in reversed(db):
        if ((tag in x['item']['tag']) and (x['item']['level'] == 1)):
            served = True
            outHtml.html.body.div.insert_after(Soup(x['item']['content'],"html.parser"))
    if served:
        toPrinter = outHtml.prettify("utf-8")
        with open(dirOut + "_tag_" + tag.strip("#")  + "_1.html", "wb") as file:
            file.write(toPrinter)
            
# one html file containing all content with no-tag. Only first priority
tag = "_no-tag_1"
outHtml = Soup(outBase,"html.parser")
outHtml.html.head.meta.title.string = tag
outHtml.html.body.div.p.string = tag
for x in reversed(db):
    if ((x['item']['tag'] == []) and (x['item']['level']==1)):
       outHtml.html.body.div.insert_after(Soup(x['item']['content'],"html.parser"))
toPrinter = outHtml.prettify("utf-8")
with open(dirOut + tag + ".html", "wb") as file:
    file.write(toPrinter)

# one html file for all content
outHtml = Soup(outBase,"html.parser")
outHtml.html.head.meta.title.string = tag
outHtml.html.body.div.p.string = tag
for x in reversed(db):
    outHtml.html.body.div.insert_after(Soup(x['item']['content'],"html.parser"))
toPrinter = outHtml.prettify("utf-8")
with open(dirOut + "_all" + ".html", "wb") as file:
    file.write(toPrinter)
    
# end