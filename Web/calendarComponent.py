from icalendar import Calendar, Event
from datetime import datetime, timedelta

def createCalendar():
    cal =  Calendar()
    
    cal.add('prodid', '-//USPN//CoVoitUniv//FR')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')

    return cal


def addEvent(cal, uid, dtstart, summary, description, location):

    event = Event()
    event.add('uid', uid)
    event.add('dtstamp', datetime.now())
    event.add('dtstart', dtstart)
    event.add('dtend', dtstart + timedelta(minutes=30))
    event.add('summary', summary)
    event.add('description', description)
    event.add('location', location)

    cal.add_component(event)

    print(event)

    return event

def loadWeek(cal, monday, friday):
    for component in cal.walk():
        if component.name == "VEVENT":
            dtstart = component.get("dtstart").dt
            dtend = component.get("dtend").dt

            print("Start:", dtstart)
            print("END:", dtend)
    


if __name__ == "__main__":
    cal = createCalendar()

    addEvent(cal,"test", datetime.now(), "this is a summary", "this is a desciption", "this will be a location")

    loadWeek(cal, None, None)