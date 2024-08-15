import os 

from pprint   import pprint
from datetime import datetime
from datetime import timedelta

error_log           = []
telementry_readings = {}
batt_readings       = []
tstat_readings     = []

def record_telementry_reading(telementry_reading, telementry_readings, batt_readings, tstate_readings):
    
    # record all readings, and add the batt readings to one list and tstat readings to one list

    satelite_id = telementry_reading['satellite-id']
    
    if satelite_id in telementry_readings:
         telementry_readings[satelite_id].append(telementry_reading)

    else:
        telementry_readings[satelite_id] = []
        telementry_readings[satelite_id].append(telementry_reading)

    if telementry_reading['component'] == 'BATT':
        batt_readings.append(telementry_reading)

    if telementry_reading['component'] == 'TSTAT':
        tstate_readings.append(telementry_reading)

    


def check_for_errors(telementry_readings, batt_readings, tstate_readings):
                

    # batt check
    # If for the same satellite there are three battery voltage readings that are under the red low limit within a five minute interval.
    batt_reading_count = len(batt_readings)
    
    for x in range(batt_reading_count):

        # make sure to check 3 items at a time and to not go over the total number of batt readings in the list
        if x + 2 >= batt_reading_count:
            break

        first_batt_time = datetime.strptime(batt_readings[x]['timestamp'],     '%H:%M:%S.%f')
        third_batt_time = datetime.strptime(batt_readings[x + 2]['timestamp'], '%H:%M:%S.%f')

        # calculate difference in time
        # timedelta object returned only holds seconds and miliseconds
        # conversion of milliseconds to seconds is miliseconds/1000000, conversion of seconds to minutes is seconds/60 
        # total time calculated using these conversions - added the miliseconds -> seconds to the existing seconds 
        # and then divided the seconds by 60

        subtracted_time = third_batt_time - first_batt_time
        time_difference_in_minutes = (subtracted_time.seconds + (subtracted_time.microseconds/1000000))/60
        if time_difference_in_minutes < 5:
            if batt_readings[x]['raw-value'] < batt_readings[x]['red-low-limit'] \
            and batt_readings[x + 1]['raw-value'] < batt_readings[x + 1]['red-low-limit'] \
            and batt_readings[x + 2]['raw-value'] < batt_readings[x + 2]['red-low-limit']:
                # error found, record entry and move to next item
                entry_item = {
                    'satelliteId': batt_readings[x]['satellite-id'], 
                    'severity':'RED LOW', 
                    'component': 'BATT', 
                    'timestamp': batt_readings[x]['timestamp']
                }

                error_log.append(entry_item)
                break 


    # If for the same satellite there are three thermostat readings that exceed the red high limit within a five minute interval.
    tstat_reading_count = len(tstate_readings)

    for x in range(tstat_reading_count):

        # make sure to check 3 items at a time and to not go over the total number of tstat readings in the list
        if x + 2 > tstat_reading_count:
            break

        first_tstat_time = datetime.strptime(tstate_readings[x]['timestamp'],     '%H:%M:%S.%f')
        third_tstat_time = datetime.strptime(tstate_readings[x + 2]['timestamp'], '%H:%M:%S.%f')

        # see time conversion explination above in the time conversion for batt section
        subtracted_time = third_tstat_time - first_tstat_time
        time_difference_in_minutes = (subtracted_time.seconds + (subtracted_time.microseconds/1000000))/60

        if time_difference_in_minutes < 5:
            if tstate_readings[x]['raw-value'] > tstate_readings[x]['red-high-limit'] \
            and tstate_readings[x + 1]['raw-value'] > tstate_readings[x + 1]['red-high-limit'] \
            and tstate_readings[x + 2]['raw-value'] > tstate_readings[x + 2]['red-high-limit']:
                # error found, record entry and move to next item
                entry_item = {
                    'satelliteId': tstate_readings[x]['satellite-id'], 
                    'severity':'RED HIGH', 
                    'component': 'TSTAT', 
                    'timestamp': tstate_readings[x]['timestamp']
                }
                error_log.append(entry_item)
                break


# datarow format: <timestamp>|<satellite-id>|<red-high-limit>|<yellow-high-limit>|<yellow-low-limit>|<red-low-limit>|<raw-value>|<component>
with open(f'{os.getcwd()}/sample-data.txt') as file:

    for row in file:
        time_stamp = row.split(' ')[0]
        row_split  = row.split(' ')[1].split('|')

        current_data_entry = {}
        current_data_entry['timestamp']         = row_split[0]
        current_data_entry['satellite-id']      = row_split[1]
        current_data_entry['red-high-limit']    = row_split[2]
        current_data_entry['yellow-high-limit'] = row_split[3]
        current_data_entry['yellow-low-limit']  = row_split[4]
        current_data_entry['red-low-limit']     = row_split[5]
        current_data_entry['raw-value']         = row_split[6]
        current_data_entry['component']         = row_split[7].replace('\n','')

        record_telementry_reading(current_data_entry, telementry_readings, batt_readings, tstat_readings)
        

check_for_errors(telementry_readings, batt_readings, tstat_readings)
pprint(error_log)
        