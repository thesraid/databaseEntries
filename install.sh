#!/bin/bash
# Short script to install databaseEntries
# SCript has no error echecking. Please run as root from the extracted directory

echo "Starting installation"
mkdir /opt/databaseEntries
cp insert-20150824.sql.gz /opt/databaseEntries
cp databaseEntries.py /opt/databaseEntries
cp databaseEntries /etc/init.d/
chmod 755 /etc/init.d/databaseEntries
update-rc.d databaseEntries defaults
echo "Install script complete"
echo "Please run the following to test the installation:"
echo " "
echo "service databaseEntries start"
echo " "
