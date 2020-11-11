# Covid-Map

# HTML and Javascript readme




# Python files readme

The Python files pull data from sources and analyze them to create .js file for reading by the above.

To creat the .js file, do:

python3 main.py -t -s "all" -js

Note that this will ask the user if they really want to update. Say "Yes" or "Y" if you want to.

To use an existing data previously downloaded, do

python3 main.py -t -s "all" -js -updateAsOf "YYYY-MM-DD"

where the "YYYY-MM-DD" is the date of the last download.

