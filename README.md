# Path emergence simulation
### Simulation designed for answering the question on what basis and how people are creating shortcuts when roaming the  urban jungle


## Configuration

### Linux

1. run `curl -sSL https://install.python-poetry.org | python3 -` (downloads poetry)
2. check if it is added to your path (`poetry --version`), and run if is not present `export PATH="$HOME/.local/bin:$PATH"`
3. run `poetry config virtualenvs.in-project true`
4. run `poetry add <module name>` to add module to toml file, example: `poetry add numpy`
5. run `poetry install` or `poetry install --no-root` - creates env and downloads listed modules in .toml file
6. run `poetry shell` - to activate the env
7. run `poetry run python <python file>` - starts the program, example: `poetry run python main.py` 

### Windows
0. SKIP STEP 1 AND 2 IF YOU WISH TO SAVE YOUR SANITY JUST RUN `pip instaall poetry`
1. run `(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -`
2. check if it is added to your path (`poetry --version`), and add it manually to path variables should be somewhere in Appdata/Roaming/Python/Scripts
3. follow the same steps from Linux config from point 3 onwards

### Your own env is also ok