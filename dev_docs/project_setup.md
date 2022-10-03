# Project setup

## Checkout the base project

```bash
# https://stackoverflow.com/questions/651038/how-do-i-clone-a-git-repository-into-a-specific-folder
# check out the project in a directory named ./python-base
git clone git@github.com:DonalChilde/python-base.git
# use the current directory as the project directory
git clone git@github.com:DonalChilde/python-base.git .
# checkout the project in a new directory
git clone git@github.com:DonalChilde/python-base.git ./new_logbook-parser
```

## Remove the old .git directory

```bash
# specify actual path to the ,git directory
rm -rf ./.git
```

## Update dev-tool.sh

Download and configure dev-tool.sh bash script

```bash
# From the project root directory, download the script to a subdirectory.
curl --create-dirs -O --output-dir ./scripts https://raw.githubusercontent.com/DonalChilde/dev-tool/main/scripts/dev-tool.sh

# Then make executable
chmod u+x ./scripts/dev-tool.sh

# Generate an .env config file in the script directory,
# and fill in the path to the project directory.
./scripts/dev-tool.sh generate-env ./scripts

```

If this is the first time using dev-tool.sh, or the commands have changed.

```bash
# Install/Update bash completions if desired
./scripts/dev-tool.sh completions ~/.bash_completions

# inspect the ~/.bashrc
cat ~/.bashrc | more

# and add to ~/.bashrc if command is not present already
echo "source ~/.bash_completions/dev-tool.completion" >> ~/.bashrc
```

## Update project placeholder values

See placeholders.md for a list of placeholder values and their locations.
Multi-file find and replace should make quick work of this.
Remember to use case sensitive search.

## Initialize the project venv

This will also update pip, setuptools, and pip-tools.

```bash
./scripts/dev-tool.sh venv-init
```

## Compile and install the project requirements, install the project as editable

```bash
./scripts/dev-tool.sh deps-compile
./scripts/dev-tool.sh deps-init
```

## Init and configure git

```bash
git init
./scripts/dev-tool.sh scm-precommit-install
./scripts/dev-tool.sh scm-precommit-update
git add .
git commit -m "First commit"
# create a new project on github, and copy the remote repository URL
git remote add origin  <REMOTE_URL>
git remote -v
```
