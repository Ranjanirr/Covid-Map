var prevState = 0;
var createStateData = function(name, partyColor)
{
  var stateData = {}; //creates an object that stores the name of the data and the data itself
  stateData.name = name;
  stateData.theResults = null;
  return stateData;
  
};
/*Function that changes the table whenever a state is moused over, called in map.js*/
var setStateResults = function(state)
{
  theStates[prevState].rgbColor = [175,175,175];
  
  theStates[state].rgbColor = [11, 32, 57];
 
  prevState = state;
  var stateInfoTable = document.getElementById('stateResults');
  var header = stateInfoTable.children[0].children[0];
  header.children[0].innerText = theStates[state].nameFull;
  header.children[1].innerText = theStates[state].nameAbbrev;
  var infectionData = stateInfoTable.children[1].children[0];
  var contactData = stateInfoTable.children[1].children[1];
 
  infectionData.children[0].innerText = "Infection Probability Percent";
  infectionData.children[1].innerText = infection.theResults[state]
  contactData.children[0].innerText = "Contact Budget";
  contactData.children[1].innerText = contact.theResults[state]

};
//Initiates the original objects for infection and contact
var infection = createStateData("Infection Probability", [132, 17, 11]);
var contact = createStateData("Contact Budget", [245, 141, 136]);
//Gets results from the json and stores them in variables
var obj = JSON.parse(JSON.stringify(results));
//var obj = JSON.parse(results);
infection.theResults = obj.InfChance;
contact.theResults = obj.ContactBudget;




/**
WASTE OF SPACE

**/