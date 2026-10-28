Previous version gave the option to user to select a year and a month and see the graph of total counts for a letter in that month and year.
Updated this to:
	Make selection of month optional (index.html)
	When month is not selected,  get answers for the whole year, and show the letter counts for those answers (flax.app)


Further changes / updates
	Showing table of counts instead of the graph
		The table will have counts of occurrence for each letter in each of the 5 places of the 5 letter wordle answer
	Each letter(index column) and letter position(column names) have a button that can be clicked.
	When a letter button is clicked, it shows the graph for the counts of that letter in each of the 5 places(on a separate page)
	When a position button is clicked, it shows the graph for the counts of the letters in that position (on a separate page)

--------------------------------
After testing on PythonAnywhere:
--------------------------------
session variables seem to have caused confusion which was not visible when running locally.
So, used global variables instead of session variables.
