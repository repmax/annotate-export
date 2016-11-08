# -*- coding: utf-8 -*-

"""===============================================
xZotHtml()
Python 3.5
_______________________________________________
DESCRIPTION
Given a tag (myTag) the script will enquire Zotero's api and get content for all relevant entities.
The extracted annotations are restructured to better show relationship between markup and notes.
It also allows for tags and images to be assigned.
The function output a list of objects where each object is a markup.
_______________________________________________
EXAMPLES

zot = zotero.Zotero(keys['library_id'], keys['library_type'], keys['api_key'])
db = xzh.ripZotApi(zot,myTag,attachDir)
==============================================="""

from bs4 import BeautifulSoup as Soup
import copy
import datetime
from pyzotero import zotero
import json

"""
Helper functions
"""
def commentSplit (comment):
    comment = comment.strip()
    modString = []
    tags = []
    image = ''
    # parsing comment
    for word in comment.split():
        if word.startswith("img@"):
            if ('http' in word):
                filePath = word.replace('img@','')
            else:
                filePath = 'file:///Z:/' + word.split('@Z',-1)[1]
            image = filePath
        elif word.startswith("#"):
            tags.append(word)
        else:
            modString.append(word.strip())
    output = {'comment':' '.join(modString),'tags':tags, 'image':image}
    return output

def pTags (tagList):
    newTag = Soup('<p></p>',"html.parser")
    newTag.p['class'] = 'tags'
    newTag.p.string = ' '.join(tagList) 
    return newTag
    
def pImg (imgUrl,level):
    newTag = Soup('<p></p>',"html.parser")
    newTag.p['class'] = 'image' + str(level)
    newTag.p.append(newTag.new_tag("a", href=imgUrl, target="_blank"))
    newTag.p.a.append(newTag.new_tag("img", src=imgUrl, style="max-height:500; max-width:500;"))  
    return newTag
    
def pComment (comment):
    newTag = Soup('<p></p>',"html.parser")
    newTag.p['class'] = 'comment'
    newTag.p.string = comment
    return newTag
    
def pHighlight (markup,level):
    newTag = Soup('<p></p>',"html.parser")
    newTag.p['class'] = 'highlight' + str(level)
    newTag.p.string = markup
    return newTag
    
def pNote (comment,level):
    newTag = Soup('<p></p>',"html.parser")
    newTag.p['class'] = 'note' + str(level)
    newTag.p.string = comment 
    return newTag

def pReferZot (ref,srcLink):
    newTag = Soup('<p></p>',"html.parser")
    newTag.p['class'] = 'ref'
    newTag.p.append(newTag.new_tag("a", href=srcLink, target="_blank"))
    # page = srcLink.rsplit('/',1)[-1]
    newTag.p.a.append(ref)      
    return newTag

"""
Main function
"""
def ripZotApi(zot,myTag,attachDir):
    tagged = zot.items(tag=myTag) # works
    newBatch = []
    for item in tagged:
        print(item['key'] +"...."+ item['data']['title'])
        children = zot.children(item['key'])
        noteNotFound = True
        attachNotFound = True
        for child in children:
            print(child['data']['itemType'])
            try:
                if child['data']['itemType'] == 'note':
                    print(" check A" )
                    note = child['data']['note']
                    if 'Extracted' in note[:100]:
                        print(" check B" + child['data']['dateAdded'])
                        dt = datetime.datetime.strptime(child['data']['dateAdded'], "%Y-%m-%dT%H:%M:%SZ")
                        if noteNotFound:
                            noteDate = dt
                            latestNote = child
                            noteNotFound = False
                        else:
                            if (noteDate < dt):
                                noteDate = dt
                                latestNote = child
                elif child['data']['itemType'] == 'attachment':
                    if child['data']['contentType'] == "application/pdf":
                        dt = datetime.datetime.strptime(child['data']['dateAdded'], "%Y-%m-%dT%H:%M:%SZ")
                        if attachNotFound:
                            attachDate = dt
                            latestAttach = child
                            attachNotFound = False
                        else:
                            if (attachDate < dt):
                                attachDate = dt
                                latestAttach = child                       
            except:
                continue
        if (noteNotFound | attachNotFound):
            continue

        # SETTING variables  
        mainSrc = {
            'srcID': latestNote['data']['parentItem'],
            'srcType':'zotfile',
            'srcBook': latestAttach['data']['title'].rsplit('.',1)[0][:38],
            'timeCreated': latestAttach['data']['dateModified'],
            }
        if latestAttach['data']['path'].startswith('attachments'):
            mainSrc['linkBook'] = 'file://' + attachDir + latestAttach['data']['path'].split(':',1)[-1]             
        else:
            mainSrc['linkBook'] = 'file://' + latestAttach['data']['path']       
            
        mainItem = {
            'timeMod': latestNote['data']['dateModified']
            }  
        # make string into an xml object    
        soup = Soup(latestNote['data']['note'],"html.parser")  
        divList = soup.find_all('div')    
        divList.reverse() # needed to check for comment before highlight
        # PARSING the latest "Extracted Annot"
        for idx, inDiv in enumerate(divList):
            # determine class
            tags = []
            divSoup = Soup('<div></div>',"html.parser")
            div = divSoup.div # needed to insert stuff within 'div' tag
            try:
                classType = inDiv['class'][0] # 'class' is a multi-valued attribute and is returned as a list ('id' is a string)
            except:
                continue
            if (classType == 'note'):
                try:
                    cSplit = commentSplit(inDiv.find('p', class_='text').get_text(" ", strip=True))
                    tags = cSplit['tags']
                    # yellow, green
                    if any(x in inDiv['style'] for x in ['255,255,0','ffff00','0,255,0','00ff00']): 
                        commentStored = True
                        continue
                    # fucasia
                    elif any(x in inDiv['style'] for x in ['255,0,255','ff00ff','d500f9']):
                        level = 1
                    # cyan 
                    elif any(x in inDiv['style'] for x in ['0,255,255','00ffff','00b0ff']):
                        level = 2
                    else:
                        continue
                    if cSplit['image'] != '':    
                        noteType = 'image'
                        div.append(pImg(cSplit['image'],level))
                        if (cSplit['comment']) != '':
                            div.append(pComment(cSplit['comment']))  
                    else:
                        noteType = 'note'
                        if (cSplit['comment']) != '':
                            div.append(pNote(cSplit['comment'],level))
                except:
                    print("note except")
                    raise
                    continue       
            elif (classType == 'highlight'):
                try:
                    if any(x in inDiv['style'] for x in ['255,255,0','ffff00']):
                        level = 1
                    elif any(x in inDiv['style'] for x in ['0,255,0','00ff00']):
                        level = 2
                    else:
                        continue
                    noteType ='highlight'
                    try:
                        if commentStored:
                            tags = cSplit['tags']
                            if (cSplit['comment']) != '':
                                div.append(pComment(cSplit['comment']))
                            commentStored = False
                    except:
                        pass            
                    text = inDiv.find('p', class_='text').text
                    if text != '':
                        div.insert(0,pHighlight(text,level))
                except:
                    print("highlight except")
                    raise
                    continue                     
            else:
                continue                  
            # will only run below if either 'note' or ' highlight' was successful                      
            # adding div and output objects  
            if tags != []:           
                div.insert(0,pTags(tags))
            src = copy.copy(mainSrc)
            src['page'] = inDiv.find('a').text.rsplit(':',1)[-1]
            src['line'] = len(divList) - idx
            item = copy.copy(mainItem)
            item['itemType'] = noteType
            item['level'] = level
            item['tag'] = tags
            item['content'] = str(div)     
            item['link'] = src['linkBook'] + '#page=' + src['page'] # file://D://raw//test.pdf#page=4    
            ref = src['srcBook'] + ':' + src['page']        
            div.insert(0,pReferZot(ref,item['link']))
            item['content'] = str(div)
            newBatch.append({'src':copy.copy(src),'item':copy.copy(item)})         
    # Lets put the list back into its natural order
    newBatch.reverse() 
    return newBatch
