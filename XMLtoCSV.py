import re, os
from datetime import datetime, date
import xml.etree.ElementTree as ET
ET.register_namespace('', "http://www.topografix.com/GPX/1/1")

# aby to bezelo z adresare, zdroj https://stackoverflow.com/questions/29553668/script-running-in-pycharm-but-not-from-the-command-line
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))


#cesta k adresari skriptu
path = (os.path.dirname(os.path.realpath(__file__)))

#najde vsechny soubory xml v adresari a parsne je
for filename in os.listdir(path):
    if filename.endswith('new.xml'):
        break
    else:
        if not filename.endswith('.xml'): continue
        fullname = os.path.join(path, filename)
        nfilename=filename
        tree = ET.parse(fullname)

#vytvoreni noveho jmena pro koncove xml
nfullname = path + '\\' + nfilename[:-4] + '_new' + '.xml'
root = tree.getroot()



# prvni cas v XML
#print(root[0][3][0][1].text)
frtime= datetime.strptime(re.search(r'\d{2}:\d{2}:\d{2}.\d{3}', (root[0][3][0][1].text)).group(),'%H:%M:%S.%f').time()

#filtrovani vsech casu
ns = {'':'http://www.topografix.com/GPX/1/1'}
timelist = []   #seznam casu po sekunde
for x in root.findall('.//time', ns):
    #ulozi vsechny datumy do fulldate ve formatu textu
    fulldate = (x.text)
    #time = re.search(r'\d{2}:\d{2}:\d{2}.\d{3}', fulldate).group()
    #ulozi do time cas ve formatu casu H:M:S:f
    time = datetime.strptime(re.search(r'\d{2}:\d{2}:\d{2}.\d{3}', fulldate).group(),'%H:%M:%S.%f').time()

    #rozdil casu
    rozdil = datetime.combine(date.min, time) - datetime.combine(date.min, frtime)
    rozdilint= rozdil.seconds + rozdil.microseconds/1000000

    #vyfiltruje casy po sekunde a prida je do seznamu timelist
    if rozdilint > 1 or rozdilint == 0:
        timelist.append(time.strftime('%H:%M:%S.%f'))
        frtime=time
    else:
        pass


#vymazani trackpointu jejichz cas neni v seznamu


targets = root[0].find('trkseg', ns)
newtimelist = [x[:-3] for x in timelist] # vymaze z timelistu posledni tri cislice

set = False # prepinac urcujici jestli polozka z newtimelist je v time_l
for target in targets.findall('trkpt', ns):
    time_l = target.find('time', ns)

    for x in newtimelist:
        if time_l is not None and x in time_l.text:
            set = True # pokud je polozka z newtimelist v time_l tak nastavi na True

    if set == False: # pokud je set False, polozka z newtimelist neni v aktualnim time_l a smaze se trkpt
        targets.remove(target)

    set = False # nastavi prepinac zpet a cyklus jede znovu

tree = ET.ElementTree(root)
tree.write(nfullname)

###########################################################################
#vytvoreni csv souboru

import csv, itertools
with open(nfilename[:-4] + '.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["ID","trksegID","lat","lon","ele","time"])
    trseg_id= 0
    for track_point in root.findall('.//trkpt', ns):
        trseg_id += 1
        lat_csv = track_point.attrib['lat']
        lon_csv = track_point.attrib['lon']
        ele_csv = track_point.find('ele', ns).text
        time_csv = track_point.find('time', ns).text
        print(1,trseg_id, lat_csv, lon_csv, ele_csv, time_csv)
        writer.writerow([1, trseg_id,lat_csv,lon_csv, ele_csv, time_csv])


'''
for elem in root:
    for subelem in elem:
        for subelem in subelem:
            for subelem in subelem:
                print(subelem.text)
'''
