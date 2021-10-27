## Installing the dependencies
In order to install the dependencies, simply run the following from the root of the folder:
```commandline
pip install -r requirements.txt
```

## Running the code
Before running the code, make sure to set the correct PYTHONPATH from project root:  

on windows:  
```commandline
$env:PYTHONPATH = "$pwd;$env:PYTHONPATH"
```
on linux:
```commandline
export PYTHONPATH="$(pwd):$PYTHONPATH"
```
Both parties are represented by the same main file. In order to execute the protocol simply open two 
terminal windows (or create a batch script, I was too lazy to do that) and run the following line:
```commandline
python .\main.py number_of_throws=5 starting=0
```
IMPORTANT NOTE: The `number_of_throws` for both parties must be the same for both commands, otherwise 
one of the terminal windows will just wait indefinitely

The `starting` value must be set to 0 in one terminal, and to 1 (or anything that is not 0) in the 
other terminal. This is because we need a way to establish who starts the game. 
