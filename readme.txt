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
		. virtualenv/bin/activate
	- install dependencies
		pip install -r requirements.txt

How to run:
1. Run the gg_api.py script
	python gg_api.py
2. This will call the pre_ceremony() function, followed by main()
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
