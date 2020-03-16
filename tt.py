from datetime import datetime, timedelta
from pytz import timezone
import time
import pytz

pacific_tz = timezone('US/Pacific')

values = [
   {"time":"06:30", "value":"on"},
   {"time":"20:00", "value":"off"}]

def get_current_value(values, current): 
   idex = 0
   sorted_times = sorted(values, key = lambda i: i['time']) 
   print(sorted_times)
   for val in sorted_times:
      if(current<int(val['time'].replace(':',''))):
         current_value = sorted_times[idex-1]['value']
         return current_value

      idex+=1

def current_time(tz):
   fmt = '%H:%M'

   loc_dt = datetime.now(tz)
   print("current time: ",loc_dt.strftime(fmt))

   current = int(loc_dt.strftime(fmt).replace(':',''))
   return current

def convert_localtime_to_gmt(timeval, local_tz):
   all_date = "{0} {1}:00".format(datetime.now().strftime("%Y-%m-%d"), timeval)
   naive = datetime.strptime(all_date, "%Y-%m-%d %H:%M:%S")
   local_dt = local_tz.localize(naive, is_dst=None)
   utc_dt = local_dt.astimezone(pytz.utc)
   return utc_dt

for val in values:
   utc_dt = convert_localtime_to_gmt(val['time'], pacific_tz)
   print(utc_dt.strftime("%H:%M"))

current = current_time(pacific_tz)
current_value = get_current_value(values, current)
print('current value: {0}'.format(current_value))
