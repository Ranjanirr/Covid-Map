# Covid-Map

# HTML and Javascript readme

How to run the program:
1) Follow the same instructions that is on the Python files readme
2)Click on corona-program.html and it should show an interactive COVID map on a web page

About html = it organizes the layout of the file, at the top, a title and legend and and allows access to scripts for the map (from an outside source) javascript and the javascript that Ranjani wrote that can edit data based on a state hovered. The HTML has a table that updates its rows according to the state and the data based on the state hovered on the map. 

About javascript = parses the results into an object with keys as the data categories and values as the data sets for the categories. Its primary function is called in the map javascript. The map javascript identifies the state hovered and calls the function Ranjani wrote- which is responsible for updating the state table with the COVID data for that particular state. 

The html and javascript files' main purpose is to visualize the coronavirus data calculated by Ram's model. 

# Python files readme

The Python files pull data from sources and analyze them to create .js file for reading by the above.

To creat the .js file, do:

python3 main.py -t -s "all" -js

Note that this will ask the user if they really want to update. Say "Yes" or "Y" if you want to.

To use an existing data previously downloaded, do

python3 main.py -t -s "all" -js -updateAsOf "YYYY-MM-DD"

where the "YYYY-MM-DD" is the date of the last download.

