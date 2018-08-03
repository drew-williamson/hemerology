import csv

from bs4 import BeautifulSoup
import requests

# make a dictionary of month names and numerical representations
month_dict = {'January': '01',
             'February': '02',
             'March': '03',
             'April': '04',
             'May': '05',
             'June': '06',
             'July': '07',
             'August': '08',
             'September': '09',
             'October': '10',
             'November': '11',
             'December': '12'}


def get_all_calendar_items(soup):
    data = []
    rows = soup.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele]) # Get rid of empty values
    data = [item for item in data if len(item) > 0]
    return data


def get_bold_calendar_items(soup):
    data_bold = []
    rows = soup.find_all('tr')
    emboldened = soup.find_all(style='font-weight:bold')
    for row in emboldened:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data_bold.append([ele for ele in cols if ele is not ''])
    data_bold = [item for item in data_bold if len(item) > 0]
    return data_bold


def construct_calendar_dictionary(items):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    am_pm = ['AM', 'PM']
    cal_dict = {}
    for i, row in enumerate(items):
        if len(row) == 1:
            if row[0].split(',')[0] in days:
                cal_dict[row[0]] = []
                curr_date_index = i
        if len(row) in [3, 4]:
            if row[0][0] in str(list(range(0,10))) and '\n' not in row[0]:
                cal_dict[items[curr_date_index][0]].append(row)
    return cal_dict


def filter_out_non_bolds(cal_dict, bold_events):
    filtered_cal_dict = {}
    for day, events in cal_dict.items():
        filtered_cal_dict[day] = []
        for event in events:
            if event in bold_events:
                filtered_cal_dict[day].append(event)
    return filtered_cal_dict


def construct_and_write_calendar_files(cal_dict, bold: bool):
    if bold:
        filename = 'bold_only_events.csv'
    else:
        filename = 'all_events.csv'
    
    with open(filename, 'w') as csvfile:
        cal_writer = csv.writer(csvfile)
        
        # write the header of the csv
        cal_writer.writerow(['Subject',
                             'Start Date', 'Start Time',
                             'End Date', 'End Time'
                             'Description', 'Location'])
        
        for date, events in cal_dict.items():
            # create the correct date format for all events within a day
            parts = date.split(',')
            year = parts[2][1:]
            month_day = parts[1].split(' ')
            month = month_dict[month_day[1]]
            day = month_day[2]
            date_combined = year + '/' + month +'/' + day
            
            # set the components of the csv for each event
            for j, event in enumerate(events):
                # subject
                subject = event[1]
                
                # start datetime
                start_date = date_combined
                start_time = event[0]
                
                # end datetime
                end_date = date_combined
                if event[0][-2] == 'A' and event[0][:2] == '11':
                    end_time = '12:00 PM'
                else:
                    split_time = start_time.split(':')
                    hour = split_time[0]
                    minute = split_time[1][:2]
                    end_time = str(int(hour) + 1) + minute
                    
                # description
                if len(event) == 4:
                    description = event[2].replace('\n', '')
                else:
                    description = ''
                
                # location
                location = event[-1]
                
                cal_writer.writerow([subject,
                                     start_date, start_time,
                                     end_date, end_time,
                                     description, location])

                
# load the page
page = requests.get("http://bwhpathology.partners.org/Calendar.aspx")

# parse with BeautifulSoup
soup = BeautifulSoup(page.content, 'html5lib')

# gather all events and only those in bold
events = get_all_calendar_items(soup)
bold_events = get_bold_calendar_items(soup)

# create dictionaries of the events
cal_dict = construct_calendar_dictionary(events)
bold_cal_dict = filter_out_non_bolds(cal_dict, bold_events)

# build and write the csvs with the events
construct_and_write_calendar_files(cal_dict, bold=False)
construct_and_write_calendar_files(cal_dict, bold=True)
