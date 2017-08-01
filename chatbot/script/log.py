# /usr/bin/python2.7
# I'm the log buddy. I log things !


DJANGO_LOGGING = True # I'm only implementing this lazily here, but we'd stick this constant in the settings.py of the parent app and all it into necessary pages.

def PrintException():
    import linecache
    import sys
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    return 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)



def log_exception(err, filename="general_log.txt", exception=False):
    if DJANGO_LOGGING:
        import time
        import datetime
        import os
        errorFile = open(os.path.join(os.path.dirname(__file__), 'errors', filename), "a")
        startTime = time.time()
        startTime = datetime.datetime.fromtimestamp(startTime) # check 
        errorFile.write("Time: " + str(startTime) + "  ")
        errorFile.write(str(err))
        if exception:
            errorFile.write("\n" + PrintException())
        errorFile.write("\n")
        errorFile.close()

def log_modified_time(filepath, errorfilename="error_file.txt"):
    if DJANGO_LOGGING:
        import time
        import datetime
        import os
        time_seconds = os.path.getmtime(filepath)
        time_struct = time.gmtime(time_seconds)
        time_formatted = time.strftime("%Y-%m-%dT%H:%M:%SZ\n", time_struct)
        errorFile = open(os.path.join(os.path.dirname(__file__), 'errors', errorfilename), "a")
        errorFile.write(str(os.path.basename(filepath)) + " was last modified: ")
        errorFile.write(str(time_formatted))
        errorFile.write("\n")
        errorFile.close()
        




## You put this chappy as a decorator in a function, and it will output run times
def profile_runspeed(func):
  def logger(*args, **kwargs):
    import json  #Imports should typically go together at the top of a file, as it is faster and each import is negligible
    import time  #But as these are debugging functions I've left this in for portability.
    import os
    import datetime
    LOGGING_LOCATION = "profile_log.txt"
    start_time = time.time()
    function_outcome = func(*args,**kwargs)
    if not DJANGO_LOGGING:
      return function_outcome
    else:
      errorFile = open(os.path.join(os.path.dirname(__file__), 'errors', LOGGING_LOCATION), "a")
      startTime = time.time()
      startTime = datetime.datetime.fromtimestamp(startTime) # check 
      errorFile.write("Time: " + str(startTime) + "  ")
      time_taken = "--- %s seconds ---" % (time.time() - start_time)
      current_function = func.__name__
      #locals_json = json.dumps(locals(), indent=2, sort_keys=True, default=str)
      errorFile.write("\nCurrent Function: " + current_function)
      errorFile.write("\nTime Taken:" + time_taken)
      errorFile.write("\nOutput: " + str(function_outcome))
      #errorFile.write("\nLocal Variables \n " + locals_json)
      errorFile.write("\n")
      errorFile.close()
      return function_outcome
  return logger
      