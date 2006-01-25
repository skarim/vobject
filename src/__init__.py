"""
VObject Overview
================
    vobject parses vCard or vCalendar files, returning a tree of Python objects.
    It also provids an API to create vCards or vCalendars data structures which
    can then be serialized.

    Parsing existing streams
    ------------------------
    Streams containing one or many L{Component<vobject.Component>}s can be
    parsed using L{readComponents<vobject.readComponents>}.  As each Component
    is parsed, vobject will attempt to give it a L{Behavior<behavior.Behavior>}.
    If an appropriate Behavior is found, any base64, quoted-printable, or
    backslash escaped data will automatically be decoded.  Dates and datetimes
    will be transformed to datetime.date or datetime.datetime instances.
    Components containing recurrence information will have a special rruleset
    attribute (a dateutil.rrule.rruleset instance).

    Validation
    ----------
    L{Behavior<behavior.Behavior>} classes implement validation for
    L{Component<vobject.Component>}s.  To validate, an object must have all
    required children.  There (TODO: will be) a toggle to raise an exception or
    just log unrecognized, non-experimental children and parameters.
    
    Creating objects programatically
    --------------------------------
    A L{Component<vobject.Component>} can be created from scratch.  No encoding
    is necessary, serialization will encode data automatically.  Factory
    functions (TODO: will be) available to create standard objects.

    Serializing objects
    -------------------
    Serialization: 
      - Looks for missing required children that can be automatically generated,
        like a UID or a PRODID, and adds them
      - Encodes all values that can be automatically encoded
      - Checks to make sure the object is valid (unless this behavior is
        explicitly disabled)
      - Appends the serialized object to a buffer, or fills a new
        buffer and returns it
    
    Examples
    --------
    
    >>> import datetime
    >>> import dateutil.rrule as rrule
    >>> x = iCalendar()
    >>> x.add('vevent')
    <VEVENT| []>
    >>> x
    <VCALENDAR| [<VEVENT| []>]>
    >>> v = x.vevent[0]
    >>> utc = icalendar.utc
    >>> v.add('dtstart').value = datetime.datetime(2004, 12, 15, 14, tzinfo = utc)
    >>> v
    <VEVENT| [<DTSTART{}2004-12-15 14:00:00+00:00>]>
    >>> x
    <VCALENDAR| [<VEVENT| [<DTSTART{}2004-12-15 14:00:00+00:00>]>]>
    >>> newrule = rrule.rruleset()
    >>> newrule.rrule(rrule.rrule(rrule.WEEKLY, count=2, dtstart=v.dtstart[0].value))
    >>> v.rruleset = newrule
    >>> list(v.rruleset)
    [datetime.datetime(2004, 12, 15, 14, 0, tzinfo=tzutc()), datetime.datetime(2004, 12, 22, 14, 0, tzinfo=tzutc())]
    >>> v.add('uid').value = "randomuid@MYHOSTNAME"
    >>> print x.serialize().replace(vobject.CRLF, vobject.LF).strip()
    BEGIN:VCALENDAR
    VERSION:2.0
    PRODID:-//PYVOBJECT//NONSGML Version 1//EN
    BEGIN:VEVENT
    UID:randomuid@MYHOSTNAME
    DTSTART:20041215T140000Z
    RRULE:FREQ=WEEKLY;COUNT=2
    END:VEVENT
    END:VCALENDAR
    
"""

import vobject, icalendar, vcard
from vobject import readComponents, readOne

def iCalendar():
    obj = vobject.Component('VCALENDAR')
    obj.setBehavior(icalendar.VCalendar2_0)
    return obj

def vCard():
    obj = vobject.Component('VCARD')
    obj.setBehavior(vcard.VCard3_0)
    return obj