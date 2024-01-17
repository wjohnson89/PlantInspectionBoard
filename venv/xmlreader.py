import xmltodict
import json
import collections
import time
import re
import sys
from datetime import datetime, timedelta

ts = time.time()
now = datetime.now()
today12pm = now.replace(hour=12, minute=0, second=0, microsecond=0)
today330pm = now.replace(hour=15, minute=30, second=0, microsecond=0)
# print(now < today12pm)
# print(now == today12pm)
# print(now > today12pm)
# todaysdate = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
todaysdate = datetime.today()
td = datetime.today().strftime('%Y-%m-%d')
td = datetime.strptime(td, '%Y-%m-%d')
# print(td)

yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
yesterday = datetime.strptime(yesterday, '%Y-%m-%d')


def readxml():
    try:
        with open('static/PlantInspectionActivity.xml') as dab:
            namespaces = {

                'PlantInspectionActivity': 'pia'
            }
            doc = xmltodict.parse(dab.read(), process_namespaces=True, namespaces=namespaces)
            # print(doc['dataroot']['PlantInspectionActivity'])
            # test = doc['dataroot']['PlantInspectionActivity']
            # j = json.dumps(test, indent=4)
            # print(j)
            return doc
    except (FileNotFoundError, IOError) as e:
        print("An error occurred trying to read the file. Quitting... \n\n\n\n")
        print(e)
        activity = []
        data = collections.OrderedDict()
        assn = collections.OrderedDict()
        assn[
            'Initials'] = 'Information is missing/incorrect in PlantInspectionActivity.xml.\n\nPlease inspect the Access database query to assure the data has been input correctly.'
        activity.append(assn)

        data['PlantInspectionActivity'] = activity
        dataroot = collections.OrderedDict()
        dataroot['dataroot'] = data

        return dataroot

'''
    XMLreader library doesn't consistently migrate data into OrderedDict instead it drops the List portion for whatever reason the developer decided.
    This function quickly formats the data to be wrapped into a list if it is a single field.
'''
def singlefieldformat(doc):
    # print("Before manipulation: ")
    # print(doc['dataroot']['PlantInspectionActivity'])

    # Add data to be manipulated to a list
    piadata = [doc['dataroot']['PlantInspectionActivity']]
    # print("\nPrint piadata: ")
    # print(piadata)

    # Replace data with List
    doc['dataroot']['PlantInspectionActivity'] = piadata
    #
    # print("\nAfter manipulated: ")
    # print(doc['dataroot']['PlantInspectionActivity'])
    # print(doc)
    return formatfile(doc)


def formatfile(doc):

    # Establish new XML file with formatted fields
    activity = []
    data = collections.OrderedDict()
    # print(doc)
    # for i in doc['dataroot']['PlantInspectionActivity']:
    #      print(i)
        # print(v)
    try:
        for i in doc['dataroot']['PlantInspectionActivity']:

            assn = collections.OrderedDict()
            # Read from original and format
            initials = i['Initials']
            # Format time
            date = i['ActivityDate']
            date = date[:10]
            # Read date and filter based on time of day.
            # i.e. if it is already past 12PM remove fields from previous day
            prsdate = datetime.strptime(date, '%Y-%m-%d')

            onsite = i['OnSiteTime']
            onsite = onsite[11:17]
            onsiteprs = re.sub(':', '', onsite)
            onsiteprs = int(onsiteprs)

            onsiteprs -= 1200

            onsitet = formattime(onsiteprs)
            ''' 
            Filter out data that falls before today at 330PM if the current time is after 12PM 
            
            '''
            onsiteprs += 1200
            # print(now)
            # print(today12pm)
            # print(now > today12pm)
            #
            # print(prsdate)
            # print(td)
            # print(prsdate < td)
            #
            # print(onsiteprs)
            # print(onsiteprs < 1530)
            # print('\n')
            # print((now > today12pm) & (prsdate <= td) & (onsiteprs < 1530))
            if (now > today12pm) & (prsdate <= td) & (onsiteprs < 1530):
                continue

            #     For testing
            # if (now < today12pm) & (prsdate < td) & (onsiteprs < 330):
            #     continue

            date = date[5:7] + '/' + date[8:10] + '/' + date[0:4]
            plant = i['Plant']
            mix = i['MIX']
            qty = i['Quantity']
            units = i['Units']
            quantity = str(qty)+' '+units
            propuse = i['ProposedUse']

            # Assign to new dict
            assn['Initials'] = initials
            assn['Date'] = date
            assn['Plant'] = plant
            assn['Mix'] = mix
            assn['Quantity'] = quantity
            assn['ProposedUse'] = propuse
            assn['OnSiteTime'] = onsitet
            activity.append(assn)
    except KeyError:
        print('Information is missing from PlantInspectionActivity.xml')
        assn = collections.OrderedDict()
        assn['Initials'] = 'Information is missing/incorrect in PlantInspectionActivity.xml.\n\nPlease inspect the Access database query to assure the data has been input correctly.'
        activity.append(assn)
    # except TypeError as e:
    #
    #     print('TypeError occurred. Trying to reformat.....')
    #     print(e)
    #     singlefieldformat(doc)


        # assn = collections.OrderedDict()
        # assn['Initials'] = 'Information is missing/incorrect in PlantInspectionActivity.xml.\n\nPlease inspect the Access database query to assure the data has been input correctly.'
        # activity.append(assn)

    data['PlantInspectionActivity'] = activity
    dataroot = collections.OrderedDict()
    dataroot['dataroot'] = data

    return dataroot


def formattime(onsiteprs):
    if onsiteprs == -1200:
        onsitet = str(onsiteprs + 2400)
        onsitet = onsitet[:2] + ':' + onsitet[2:] + ' AM'
        # print("Time is midnight: "+onsitet+"\n")

    elif onsiteprs < 0:
        onsitet = str(onsiteprs + 1200)
        if len(onsitet) == 4:
            # onsitet = '0' + onsitet
            onsitet = onsitet[:2] + ':' + onsitet[2:] + ' AM'
        elif len(onsitet) == 2:
            onsitet = '12:' + onsitet + ' AM'
            # print("Time is just after midnight: " + onsitet + "\n")
        elif len(onsitet) == 3:
            onsitet = '0' + onsitet
            onsitet = onsitet[:2] + ':' + onsitet[2:] + ' AM'
            # print(onsitet)

    elif onsiteprs == 0:
        onsitet = str(onsiteprs + 1200)
        onsitet = onsitet[:2] + ':' + onsitet[2:] + ' PM'
        # print("Time is noon: " + onsitet + "\n")

    elif onsiteprs > 0:
        onsitet = str(onsiteprs)
        if len(onsitet) <= 2:
            onsitet = str(int(onsitet) + 1200)
            onsitet = onsitet[:2] + ':' + onsitet[2:] + ' PM'
            # print("Time is 12PM something..: "+onsitet+"\n")

        elif len(onsitet) == 3:
            onsitet = '0' + onsitet[:1] + ':' + onsitet[1:] + ' PM'
            # print("Time is PM: " + onsitet + "\n")

        elif len(onsitet) == 4:
            # onsitet = '0' + onsitet
            onsitet = onsitet[:2] + ':' + onsitet[2:] + ' PM'
            # print("Time is PM: "+onsitet+"\n")

    # print("\nAfter formatting: " + onsitet)
    return onsitet


def format2xml(data):
    newdoc = xmltodict.unparse(data, pretty=True)
    try:
        file = open('static/DailyAssignments_TODAY.xml', 'w+')
        file.write(newdoc)
        file.close()
        # print(newdoc)
    except FileNotFoundError as e:
        print(e)


def run():
    print('Running XMLreader')
    doc = readxml()
    try:
        act = formatfile(doc)
    except TypeError:
        print('Single field detected... formattting...')
        act = singlefieldformat(doc)

    format2xml(act)


if __name__ == "__main__":
    run()
