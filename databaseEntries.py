#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# joriordan@alienvault.com
#
# A script to take an empty events backup file and replace it with valid events from a stored file
# This script is invoked by /etc/init.d/databaseEntries when the server starts
#
# 2015 - 08 025

import sys
from datetime import date, datetime, timedelta
from shutil import copyfile
import os
import subprocess
import syslog
import time

# http://stackoverflow.com/questions/3961581/in-python-how-to-display-current-time-in-readable-format
# print time.ctime() 

# The script receives the path to the pre-saved backup from the user 
# https://docs.python.org/2/tutorial/controlflow.html
# http://www.tutorialspoint.com/python/python_command_line_arguments.htm

if len(sys.argv) == 1:
	print " "
        print "Usage: datebaseEntries.py /path/to/valid/backup/file YYYY-MM-DD"
	print "YYYY-MM-DD is the date in the backup file that you supplied. It will be replaced with yesterdays date"
	print " "
	sys.exit()
elif len(sys.argv) == 2:
	#if sys.argv[1] == "--help":
	print " "
	print "Usage: datebaseEntries.py /path/to/valid/backup/file YYYY-MM-DD"
	print "YYYY-MM-DD is the date in the backup file that you supplied. It will be replaced with yesterdays date"
	print " "
	sys.exit()
elif len(sys.argv) == 3:
	savedBackupFile = sys.argv[1]
	oldDate = sys.argv[2]
else:
	print " "
	print "Usage: datebaseEntries.py /path/to/valid/backup/file YYYY-MM-DD : Where YYYY-MM-DD is the date to replace with yesterdays date"
	print "YYYY-MM-DD is the date in the backup file that you supplied. It will be replaced with yesterdays date"
	print " "
	sys.exit()



# Ensure the file passed by the user exists
# http://stackoverflow.com/questions/82831/check-whether-a-file-exists-using-python
if os.path.isfile(savedBackupFile):
	print(time.ctime() + " databaseEntries.py: " + savedBackupFile + " exists")
else:
	print(time.ctime() + " databaseEntries.py: " + savedBackupFile + " not found!")
	sys.exit()



# If the file is a gzipped file we will gunzip it to the /tmp directory
# http://stackoverflow.com/questions/541390/extracting-extension-from-filename-in-python
# http://stackoverflow.com/questions/4256107/running-bash-commands-in-python
filename, file_extension = os.path.splitext(savedBackupFile)
if file_extension == ".gz":
	print(time.ctime() + " databaseEntries.py: File seems to be a GZipped file. The script will Gunzip it")
	print (time.ctime() + " databaseEntries.py: Executing gunzip -f " + savedBackupFile)
	bashCommand = "gunzip -f " + savedBackupFile
	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
	output = process.communicate()[0]
	savedBackupFile = filename
	print(time.ctime() + " databaseEntries.py: File is extracted and is now called " + savedBackupFile)
	



# Ensure it's a valid SQL backup file
# http://stackoverflow.com/questions/4940032/search-for-string-in-txt-file-python
fileHandle = open(savedBackupFile, 'r+') 
if "MySQL dump" in fileHandle.read():
	print(time.ctime() + " databaseEntries.py: Seems to be a valid backup")
	fileHandle.close()
else:
	print(time.ctime() + " databaseEntries.py: Input file does not seem to be a valid MySQL Dump")
	sys.exit()
	



# Here we will get todays date in the following format
# 20150820
# http://www.cyberciti.biz/faq/howto-get-current-date-time-in-python/
# http://stackoverflow.com/questions/1712116/formatting-yesterdays-date-in-python
todaysDate = date.today()
#print ("Today is " + todaysDate.strftime("%Y%m%d"))

# Here we will get yesterdays date in the same format
yesterday = date.today() - timedelta(1)
filebackupDate = yesterday.strftime("%Y%m%d")
#print ("Yesterday was " + filebackupDate)

# Replace the dates in our backup file with yesterdays dates
newDate = yesterday.strftime("%Y-%m-%d")
print(time.ctime() + " databaseEntries.py: This script will take the inputted existing backup file and replace the event dates with " + newDate)



# Here we will open our backup file and create a copy
# We will also replace the date in our backup files with yesterdays date as we are parsing it
# We will store the copy in tmp as we will need to gzip it after
# http://stackoverflow.com/questions/4128144/replace-string-within-file-contents
dstfile = "/tmp/insert-"+filebackupDate+".sql" 
print(time.ctime() + " databaseEntries.py: Opening " + savedBackupFile  + ", changing the date " + oldDate + " to " + newDate + " and saving to " + dstfile) 
with open(dstfile, "wt") as fout:
    with open(savedBackupFile, "rt") as fin:
        for line in fin:
            fout.write(line.replace(oldDate, newDate))
print(time.ctime() + " databaseEntries.py: Dates successfully replaced")
print(time.ctime() + " databaseEntries.py: File renamed to " + dstfile)


# Gzip the copy of the file and update the dstfile variable with the new .gz extension
# http://stackoverflow.com/questions/4256107/running-bash-commands-in-python
bashCommand = "gzip -f " + dstfile
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output = process.communicate()[0]
dstfile = dstfile + ".gz"
print(time.ctime() + " databaseEntries.py: Gzipped the temp file. The file is now " + dstfile)



# Copy the now gzipped file to the backup directory 
# This will overwrite the orginal empty backup file
# http://stackoverflow.com/questions/123198/how-do-i-copy-a-file-in-python
emptyBackupfile = "/var/lib/ossim/backup/insert-" + filebackupDate + ".sql.gz"
copyfile(dstfile,emptyBackupfile) 


# All done!
print(time.ctime() + " databaseEntries.py: Successfully overwrote " + emptyBackupfile + " with " + dstfile)
print(time.ctime() + " databaseEntries.py: The system now has a backup file with yesterdays dates")
