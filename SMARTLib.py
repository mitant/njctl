# NJCTL SMARTlib
# anthony@njctl.org

from lxml import etree
import random
import string

def FindPullTabs(t, parentMap, f):
    ids = []
    
    for tspan in t.findall(".//tspan"):
        if tspan.text and (tspan.text.find("[This object") != -1 or tspan.text == "Teacher Notes"):
            parent = parentMap[tspan] # tspan
            parent = parentMap[parent] # tspan
            parent = parentMap[parent] # text
            parent = parentMap[parent] # g
            if parentMap[parent].tag == "g" and "{http://www.w3.org/XML/1998/namespace}id" in parentMap[parent].attrib:
                parent = parentMap[parent] # g
            if parent.tag == "g":
                try:
                    ids.append(parent.attrib["{http://www.w3.org/XML/1998/namespace}id"])
                except:
                    print "Problem with finding parent of pull tab in '%s'" % f
                    pass
                
    return ids

def ReplaceStringsInFile(f, pairs, n=-1):
    text = open(f).read()
    for r in pairs:
        if r[0] in text:
            if n == -1:
                text = text.replace(r[0], r[1])
            else:
                text = text.replace(r[0], r[1], n)
            # print "Updated '%s', '%s'->'%s' " % (f, r[0], r[1])

    open(f, 'w').write(text)

def IsInShortAnswerNumeric(tspan, parentMap):
    parent = parentMap[tspan]
    while parent is not None:
        try:
            if parent.tag == "g" and "class" in parent.attrib and parent.attrib["class"] == "shortanswernumeric":
                return True
        except Exception, e:
            print e
            pass
        
        if parent in parentMap:
            parent = parentMap[parent]
        else:
            break
        
    return False

def IsInPullTab(tspan, pullTabIds, parentMap):
    parent = parentMap[tspan]
    while parent is not None:
        try:
            if parent.tag == "g" and "{http://www.w3.org/XML/1998/namespace}id" in parent.attrib and parent.attrib["{http://www.w3.org/XML/1998/namespace}id"] in pullTabIds:
                return True
        except Exception, e:
            print e
            pass

        if parent in parentMap:
            parent = parentMap[parent]
        else:
            break
        
    return False

def FixDuplicateIDs(f):
    loops = 0
    validated = False
    while not validated:
        try:
            t = etree.parse(f)
            validated = True
        except Exception, e:
            loops = loops + 1
            err = "%s" % e
            id = err.split(" ")[1]
            if "annotation" not in id:
                print "Failed to parse '%s', aborting..." % f
                break
            if loops > 1000:
                print "Over 1000 loops.  Unable to auto-correct '%s', skipping.." % f
                break

            ReplaceStringsInFile(f, [[id, "annotation." + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))]], 1)

def IsInTable(tspan, parentMap):
    parent = parentMap[tspan]
    while parent is not None:
        if parent.tag == "svg" and "class" in parent.attrib and parent.attrib["class"] == "cell":
            return True

        if parent in parentMap:
            parent = parentMap[parent]
        else:
            break
            
    return False
