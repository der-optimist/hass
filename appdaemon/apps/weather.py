#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import xml.etree.ElementTree as ET
import requests, io
from openhab import openHAB
import dateutil.parser

# Input
url_dwd = "https://maps.dwd.de/geoserver/dwd/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=dwd:Warnungen_Gemeinden&CQL_FILTER=WARNCELLID%20IN%20(%27808436079%27)"
url_oh = 'http://openhabianpi:8080/rest'

# Functions
def error_loading(status_code):
    print("Fehler beim Laden der Daten. Fehlercode: " + str(status_code))
    exit()

# Start your work, python
# Load Data from DWD
response = requests.get(url_dwd)
if response.status_code == requests.codes.ok:
    xml = io.BytesIO(response.content)
else:
    error_loading(response.status_code)

# Define Namespaces and load xml data
namespaces = {
    'xs': 'http://www.w3.org/2001/XMLSchema', 
    'dwd': 'http://www.dwd.de',
    'wfs': 'http://www.opengis.net/wfs/2.0',
    'gml': 'http://www.opengis.net/gml/3.2',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
}
tree = ET.parse(xml)
root = tree.getroot()

# initialize vars
Events = []
Severities = []
Times_onset = []
Times_expires = []
EC_Groups = []
Parametervalues = []
Severities_dict = {'Extreme': 1, 'Severe': 2, 'Moderate': 3, 'Minor': 4}

# read warnings from xml
for warning in root.findall('wfs:member', namespaces):
    event = warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:EVENT', namespaces)[0].text
    if (event != "FROST") and (event != "HITZE"):
        Events.append(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:EVENT', namespaces)[0].text)
        Severities.append(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:SEVERITY', namespaces)[0].text)
        Times_onset.append(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:ONSET', namespaces)[0].text)
        Times_expires.append(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:EXPIRES', namespaces)[0].text)
        EC_Groups.append(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:EC_GROUP', namespaces)[0].text)
        Parametervalues.append(warning.findall('dwd:Warnungen_Gemeinden', namespaces)[0].findall('dwd:PARAMATERVALUE', namespaces)[0].text)
Severities_sortable = [Severities_dict.get(item,item) for item in Severities]

# write into one list and sort by severity and start time
data = []
for i in range(len(Events)):
    data.append([Severities_sortable[i], Times_onset[i], Times_expires[i], Events[i], Severities[i], EC_Groups[i], Parametervalues[i]])
data_sorted = sorted(data, key=lambda x: (x[0], x[1]))

# send values to OH
openhab = openHAB(url_oh)
Items = openhab.fetch_all_items()
for i in range(1,4):
    if i <= len(Events):
        Items.get('DWD_Warnung_' + str(i) + '_Event').state = data_sorted[i-1][3].encode('utf-8').decode('iso-8859-1')
        Items.get('DWD_Warnung_' + str(i) + '_Severity').state = data_sorted[i-1][4]
        Items.get('DWD_Warnung_' + str(i) + '_Start').state = dateutil.parser.parse(data_sorted[i-1][1])
        Items.get('DWD_Warnung_' + str(i) + '_End').state = dateutil.parser.parse(data_sorted[i-1][2])
        Items.get('DWD_Warnung_' + str(i) + '_Group').state = data_sorted[i-1][5]
        Items.get('DWD_Warnung_' + str(i) + '_Parameter').state = data_sorted[i-1][6].encode('utf-8').decode('iso-8859-1')
    else:
        Items.get('DWD_Warnung_' + str(i) + '_Event').state = '0'
        Items.get('DWD_Warnung_' + str(i) + '_Severity').state = '0'
        Items.get('DWD_Warnung_' + str(i) + '_Start').state = dateutil.parser.parse('2000-01-01T00:00:00Z')
        Items.get('DWD_Warnung_' + str(i) + '_End').state = dateutil.parser.parse('2000-01-01T00:00:00Z')
        Items.get('DWD_Warnung_' + str(i) + '_Group').state = '0'
        Items.get('DWD_Warnung_' + str(i) + '_Parameter').state = '0'
