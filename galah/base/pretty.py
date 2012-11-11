def plural_if(zstring, zcondition):
    """
    Returns zstring pluralized (adds an 's' to the end) if zcondition is True or
    if zcondition is not equal to 1.

    Example usage could be ``plural_if("cow", len(cow_list))``.

    """

    # If they gave us a boolean value, just use that, otherwise, assume the
    # value is some integral type.
    if type(zcondition) is bool:
        plural = zcondition
    else:
        plural = zcondition != 1
        
    return zstring + ("s" if plural else "")

def pretty_list(the_list, conjunction = "and", none_string = "nothing"):
    """
    Returns a grammatically correct string representing the given list. For
    example...

    >>> pretty_list(["John", "Bill", "Stacy"])
    "John, Bill, and Stacy"
    >>> pretty_list(["Bill", "Jorgan"], "or")
    "Bill or Jorgan"
    >>> pretty_list([], none_string = "nobody")
    "nobody"

    """

    the_list = list(the_list)

    if len(the_list) == 0:
        return none_string
    elif len(the_list) == 1:
        return str(the_list[0])
    elif len(the_list) == 2:
        return str(the_list[0]) + " " + conjunction + " " + str(the_list[1])
    else:
        # Add every item except the last two together seperated by commas
        result = ", ".join(the_list[:-2]) + ", "

        # Add the last two items, joined together by a command and the given
        # conjunction
        result += "%s, %s %s" % \
            (str(the_list[-2]), conjunction, str(the_list[-1]))

        return result

def pretty_timedelta(zdelta):
    # We will build our string part by part. All strings in this array will be
    # concatenated with a space as delimiter.
    stringParts = []
    
    if zdelta.days < 0:
        ago = True
        zdelta = -zdelta
    else:
        ago = False
        stringParts.append("in")

    months = abs(zdelta.days) / 30
    hours = zdelta.seconds / (60 * 60)
    minutes = (zdelta.seconds % (60 * 60)) / 60
    seconds = (zdelta.seconds % 60)

    if months == 0 and zdelta.days == 0 and hours == 0 and minutes == 0 and \
            seconds < 10:
        return "just now"
    
    # Add the months part. Because we only approximate the numbers of months,
    # the rest of the numbers (days, hours, etc) won't be exact so we skip the
    # rest of the if statements.
    if months != 0:
        stringParts += ["about", str(months), plural_if("month", months)]
    
    # Add the days part
    if months == 0 and zdelta.days != 0:
        stringParts += [str(zdelta.days), plural_if("day", zdelta.days)]
    
    # Add the hours part
    if months == 0 and hours != 0:
        stringParts += [str(hours), plural_if("hour", hours)]
    
    # Add the minutes part if we're less than 4 hours away
    if months == 0 and minutes != 0 and zdelta.days == 0 and hours < 4:
        stringParts += [str(minutes), plural_if("minute", minutes)]
        
    # Add the seconds part if we're less than 10 minutes away
    if months == 0 and seconds != 0 and zdelta.days == 0 and hours == 0 and minutes < 10:
        stringParts += [str(seconds), plural_if("second", seconds)]
            
    if ago:
        stringParts.append("ago")
    
    return " ".join(stringParts)
    
def pretty_time_distance(za, zb):
    return pretty_timedelta(zb - za)

def pretty_time(ztime):
    return ztime.strftime("%A, %B %d, %Y @ %I:%M %p")
