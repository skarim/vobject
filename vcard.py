"""Definitions and behavior for vCard 3.0"""

import behavior
import itertools

from vobject import VObjectError, NativeError, ValidateError, ParseError, \
                    VBase, Component, ContentLine, logger, defaultSerialize, \
                    registerBehavior, backslashEscape

from icalendar import TextBehavior

#------------------------ vCard structs ----------------------------------------

class Name(object):
    def __init__(self, family = '', given = '', additional = '', prefix = '',
                 suffix = ''):
        """Each name attribute can be a string or a list of strings."""
        self.family     = family
        self.given      = given
        self.additional = additional
        self.prefix     = prefix
        self.suffix     = suffix
        
    @staticmethod
    def toString(val):
        """Turn a string or array value into a string."""
        if type(val) in (list, tuple):
            return ' '.join(val)
        return val

    def __str__(self):
        eng_order = ('prefix', 'given', 'additional', 'family', 'suffix')
        return ' '.join(self.toString(getattr(self, val)) for val in eng_order)

    def __repr__(self):
        return "<Name: %s>" % self.__str__()

class Address(object):
    def __init__(self, street = '', city = '', region = '', code = '',
                 country = '', box = '', extended = ''):
        """Each name attribute can be a string or a list of strings."""
        self.box      = box
        self.extended = extended
        self.street   = street
        self.city     = city
        self.region   = region
        self.code     = code
        self.country  = country
        
    @staticmethod
    def toString(val, join_char='\n'):
        """Turn a string or array value into a string."""
        if type(val) in (list, tuple):
            return join_char.join(val)
        return val

    lines = ('box', 'extended', 'street')
    one_line = ('city', 'region', 'code')

    def __str__(self):
        lines = '\n'.join(self.toString(getattr(self, val)) for val in self.lines if getattr(self, val))
        one_line = tuple(self.toString(getattr(self, val), ' ') for val in self.one_line)
        lines += "\n%s, %s %s" % one_line
        if self.country:
            lines += '\n' + self.toString(self.country)
        return lines

    def __repr__(self):
        return "<Address: %s>" % self.__str__().replace('\n', '\\n')

#------------------------ Registered Behavior subclasses -----------------------
class VCard3_0(behavior.Behavior):
    """vCard 3.0 behavior."""
    name = 'VCARD'
    description = 'vCard 3.0, defined in rfc2426'
    versionString = '3.0'
    isComponent = True
    sortFirst = ('version', 'prodid', 'uid')
    knownChildren = {'N':         (1, 1, None),#min, max, behaviorRegistry id
                     'FN':        (1, 1, None),
                     'VERSION':   (1, 1, None),#required, auto-generated
                     'PRODID':    (0, 1, None),
                     'LABEL':     (0, None, None),
                     'UID':       (0, None, None),
                     'ADR':       (0, None, None)
                    }
                    
    @classmethod
    def generateImplicitParameters(cls, obj):
        """Create PRODID, VERSION, and VTIMEZONEs if needed.
        
        VTIMEZONEs will need to exist whenever TZID parameters exist or when
        datetimes with tzinfo exist.
        
        """
        if len(getattr(obj, 'version', [])) == 0:
            obj.add(ContentLine('VERSION', [], cls.versionString))
registerBehavior(VCard3_0, default=True)

class VCardTextBehavior(TextBehavior):
    base64string = 'B'
    
class FN(VCardTextBehavior):
    name = "FN"
    description = 'Formatted name'
registerBehavior(FN)

class Label(VCardTextBehavior):
    name = "Label"
    description = 'Formatted address'
registerBehavior(FN)

def toListOrString(string):
    if string.find(',') >= 0:
        return string.split(',')
    return string

def splitFields(string):
    """Return a list of strings or lists from a Name or Address."""
    return [toListOrString(i) for i in string.split(';')]

def toList(stringOrList):
    if isinstance(stringOrList, basestring):
        return [stringOrList]
    return stringOrList

def serializeFields(obj, order):
    """Turn an object's fields into a ';' and ',' seperated string."""
    return ';'.join([','.join(toList(getattr(obj, val))) for val in order])

NAME_ORDER = ('family', 'given', 'additional', 'prefix', 'suffix')

class NameBehavior(behavior.Behavior):
    """A structured name."""
    hasNative = True

    @staticmethod
    def transformToNative(obj):
        """Turn obj.value into a Name."""
        if obj.isNative: return obj
        obj.isNative = True
        obj.value = Name(**dict(zip(NAME_ORDER, splitFields(obj.value))))
        return obj

    @staticmethod
    def transformFromNative(obj):
        """Replace the Name in obj.value with a string."""
        obj.isNative = False
        obj.value = serializeFields(obj.value, NAME_ORDER)
        return obj
registerBehavior(NameBehavior, 'N')

ADDRESS_ORDER = ('box', 'extended', 'street', 'city', 'region', 'code', 
                 'country')

class AddressBehavior(behavior.Behavior):
    """A structured address."""
    hasNative = True

    @staticmethod
    def transformToNative(obj):
        """Turn obj.value into an Address."""
        if obj.isNative: return obj
        obj.isNative = True
        obj.value = Address(**dict(zip(ADDRESS_ORDER, splitFields(obj.value))))
        return obj

    @staticmethod
    def transformFromNative(obj):
        """Replace the Address in obj.value with a string."""
        obj.isNative = False
        obj.value = serializeFields(obj.value, ADDRESS_ORDER)
        return obj
registerBehavior(AddressBehavior, 'ADR')
    
