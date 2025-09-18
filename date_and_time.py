from datetime import datetime

now = datetime.now()

# Direct attributes
year = now.year          # current year
month = now.month        # numeric month (1–12)
day = now.day            # current day 
weekday = now.strftime("%A")   # full weekday name, e.g. "Wednesday"
month_name = now.strftime("%B") # full month name, e.g. "September"

# Time parts
hour_12 = now.strftime("%I:%M") # 12-hour format string with leading zero
minute = now.minute  #current minute
second = now.second #current seconds
ampm = now.strftime("%p") # AM / PM

curent_date_time = now.strftime("%d, %Y at %I:%M %p") # current date and time