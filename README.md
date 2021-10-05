# Running the code
Before running the code, make sure to set the correct PYTHONPATH from project root:  

on windows:  
```commandline
$env:PYTHONPATH = "$pwd;$env:PYTHONPATH"
```
on linux:
```commandline
export PYTHONPATH="$(pwd):$PYTHONPATH"
```
For each task simply issue command from the root folder:
```commandline
python tasks/[task_file].py
```
for example:
```commandline
python tasks/task1.py
```