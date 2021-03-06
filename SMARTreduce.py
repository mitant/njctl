# NJCTL SMARTreduce
# anthony@njctl.org

import zipfile
import os
import sys
import shutil
import re
import xml.etree.ElementTree as ET
import random
import string
import SMARTLib
import Image
from sets import Set
from lxml import etree

nodePrefix = "{http://www.imsglobal.org/xsd/imscp_v1p1}"
xlinkPrefix = "{http://www.w3.org/1999/xlink}"

def PNGtoJPG(f, slideN, mappings):
    t = etree.parse(f)

    n = 0
    for img in t.findall(".//image"):
        if img.attrib['%shref' % xlinkPrefix].endswith(".png") and img.attrib['%shref' % xlinkPrefix].startswith("images/clipboard"):
            pngPath = img.attrib['%shref' % xlinkPrefix]
            jpgPath = pngPath.replace(".png", ".reduced.jpg")
            
            if pngPath in mappings:
                img.attrib['%shref' % xlinkPrefix] = mappings[pngPath]
                n = n + 1
            else:
                if os.path.exists(pngPath):
                    im = Image.open(pngPath)
                    im.save(jpgPath)
                    img.attrib['%shref' % xlinkPrefix] = jpgPath
                    os.remove(pngPath)
                    mappings[pngPath] = jpgPath
                    
                    n = n + 1
                else:
                    print "Failed to convert '%s'" % pngPath
                
    if n > 0:
        print "Slide #%d(%s) Converted %d images" % (slideN, f, n)
        t.write(f)

def ProcessNotebook(file):
    workingFolder = file.replace(".notebook", "")
    with zipfile.ZipFile(file) as zf:
        zf.extractall(workingFolder)

    os.chdir(workingFolder)

    nodePrefix = "{http://www.imsglobal.org/xsd/imscp_v1p1}"
    e = ET.parse("imsmanifest.xml").getroot()
    count = 1

    mappings = {}

    for c in e.find("./*" + nodePrefix + "resource[@identifier='group0_pages']"):
        p = c.attrib['href']
        
        SMARTLib.FixDuplicateXML(p)
        fixedDupes = SMARTLib.FixDuplicateIDs(p, count)

        if fixedDupes:
            PNGtoJPG(p, count, mappings)
        else:
            print "Slide #%d (%s): Unable to process.. Please manually verify.\n" % (count, p)
            
        count = count + 1
        
    # Repack the "notebook"
    zipf = zipfile.ZipFile('../converted/%s-updated.notebook' % workingFolder, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk("."):
        for file in files:
            p = os.path.join(root, file)
            zipf.write(p)
            
    zipf.close()

    os.chdir("..")

    shutil.rmtree(workingFolder, True)


if __name__ == "__main__":
    os.chdir(sys.argv[1])
    try:
        os.mkdir("converted")
    except:
        pass
    for file in os.listdir("."):
        if file.find(".notebook") != -1:
            ProcessNotebook(file)
