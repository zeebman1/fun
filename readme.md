This is a small command line interface tool to interact with the free Star Wars api - https://swapi.co/
First you choose an api endpoint. E.g. Star Wars characters. Then you
keep choosing their attributes (e.g. hair colour > tan, homeworld: Tatooine) until 
you narrow it down to a single instance - the .name attribute of that instance is then printed.


To run it, you will need python3
and additionally packages:
[pip install] pandas 
[pip install] requests

If you need to install them for a specific version of python, do:

[python version, e.g. python3] -m pip install [package_name]

and then, just:

python3 script.py
 
