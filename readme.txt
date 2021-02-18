CS 337 Project 1: Golden Globes Tweet Mining

Github Repo:
https://github.com/batuhanergor/cs337

How to install dependencies:
1. Create a virtual environment.
	- install virtualenv 
		pip install virtualenv
	- create a new environment
		python3.6 -m venv virtualenv
	- activate your virtual environment
		source virtualenv/bin/activate
	- install dependencies
		pip install -r requirements.txt

How to run gg_api:
1. Place any json data files in the 'data' directory.
	- they should be of the form 'gg{year}.json'
2. cd into the code directory
	cd code
2. Run the gg_api.py script
	python gg_api.py
3. This will call the pre_ceremony() function, followed by main()
	- pre_ceremony() runs get_winner() for each available year,
	  writing the winners to a respective json file (if it does
	  not already exist)
 	- this is because get_presenters() makes use of the winners to
	  remove winners from the list of possible presenters. 
	  get_presenters() often returns the winner rather than the
	  presenter, and this helps remedy that
	- while main() runs, it will request user input
	- the user should input one of the suggested years,
 	  and the program will subsequently print to stdout
          the results of the tweet mining in a human-readable
          format
	- the user can then select another year to view, or
	  press 1 to quit

How to run autograder.py:
1. Place any json data files in the 'data' directory.
	- they should be of the form 'gg{year}.json'
2. Place any json answer files in the 'code' directory.
	- they should be of the form 'gg{year}answers.json'
3. cd into the code directory
	cd code
4. Run the autograder.py script with a year as an argument
	python autograder.py [year]
