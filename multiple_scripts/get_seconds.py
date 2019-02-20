import sys

def get_seconds(expression_time):
    arguments=expression_time.split(":")
    if len(arguments) == 3:
        time=int(arguments[2]) #Initialize time variable with seconds
        time+=(int(arguments[0])*3600) #Add hours converted to seconds in variable
        time+=(int(arguments[1])*60) #Add Mins converted to seconds in variable
        return time
    else:
        print("Entered expression time {} is not correct".format(expression_time))
        exit(2)

def get_time_expression(seconds_input):
    seconds_input=int(seconds_input)
    hours=(seconds_input/3600)
    mins=(seconds_input%3600)/60
    seconds=seconds_input-hours*3600-mins*60
    expression="%02d:%02d:%02d" %(hours,mins,seconds)
    return expression

entrada=sys.argv[1]
print("The input time is {}".format(entrada))
print(get_seconds(entrada))
get_time_expression(get_seconds(entrada))
