# Covid-Map

This package allows visualization of the results from a COVID model [1] on a US Map.

To visualize, the steps are as follows:

1) Run the Python script as indicated below. This creates an intermediate results (results.js)
2) Then open the html file as indicated below. This reads the results.js and displays it


# Python script

The Python files pull data from sources and analyzes them according to the model in [1] to create .js file for reading by the above.

To create the .js file, do:

python3 main.py -t -s "all" -js

Note that this will ask the user if they really want to update. Say "Yes" or "Y" if you want to.

To use an existing data previously downloaded, do

python3 main.py -t -s "all" -js -updateAsOf "YYYY-MM-DD"

where the "YYYY-MM-DD" is the date of the last download.

# HTML and Javascript readme

To run the program, click on corona-program.html and it should show an interactive COVID map on a web page

corona-program.html: It organizes the layout of the file, at the top, a title and legend and and allows access to scripts for the map (from an outside source) javascript and the javascript that Ranjani wrote that can edit data based on a state hovered. The HTML has a table that updates its rows according to the state and the data based on the state hovered on the map. 

Javascript: Parses the results into an object with keys as the data categories and values as the data sets for the categories. Its primary function is called in the map javascript. The map javascript identifies the state hovered and calls a function which is responsible for updating the state table with the COVID data for that particular state. 

The html and javascript files' main purpose is to visualize the coronavirus data calculated by the  model [1].


[1] R. Ramanathan, "Is My Grocery Store Safe: A Model for Individual Infection Probability and Estimations for COVID-19 https://sites.google.com/site/ramanathanatbbn/home/pdf/Infection_Probability_Model_v1.pdf?attredirects=0


