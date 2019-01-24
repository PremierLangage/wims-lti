#!/bin/bash

echo -e "\nChecking dependencies...\n"

# Checking if python >= 3.5 is installed
if ! hash python3; then
    echo "ERROR: Python >= 3.5 should be installed. Try 'apt install python3'"
    exit 1
fi
ver=$(python3 --version 2>&1 | sed 's/.* \([0-9]\).\([0-9]\).*/\1\2/')
if [ "$ver" -lt "35" ]; then
    echo "ERROR: Python >= 3.5 should be installed."
    exit 1
fi
echo "Python >= 3.5: OK !"

# Checking if pip3 is installed
command -v pip3 >/dev/null 2>&1 || { echo >&2 "ERROR: pip3 should be installed"; exit 1; }
echo "pip3: OK !"

# Checking if git is installed
command -v git >/dev/null 2>&1 || { echo >&2 "ERROR: git should be installed"; exit 1; }
echo "git: OK !"



# Making sure changes to wimsLTI/config.py are not pushed
git update-index --no-skip-worktree wimsLTI/config.py



# Checking if inside a python venv
if [ "$VIRTUAL_ENV" == "" ]; then
    echo ""
    INVENV=1
    echo "WARNING: We recommend you to use a python virtual environment (https://docs.python.org/3/library/venv.html)." | fold -s
    read -p "Do you want to continue outside a virtual environment ? [Y/n] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]
    then
        exit 1
    fi
fi



# Getting requirement
echo ""
echo "Installing requirements..."
pip3 install wheel  || { echo>&2 "ERROR: pip3 install wheel failed" ; exit 1; }
pip3 install -r requirements.txt || { echo>&2 "ERROR: pip3 install -r requirements.txt failed" ; exit 1; }
echo "Done !"



# Building database
echo ""
echo "Configuring database..."
python3 manage.py makemigrations || { echo>&2 "ERROR: python3 manage.py makemigrations failed" ; exit 1; }
python3 manage.py migrate || { echo>&2 "ERROR: python3 manage.py migrate failed" ; exit 1; }




# Creating super user
echo
read -p "Creating a super user for django ? [y/n] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Creating super user account..."
    python3 manage.py createsuperuser || { echo>&2 "ERROR: python3 manage.py createsuperuser failed" ; exit 1; }
fi

echo "Run 'python3 manage.py createsuperuser' to create super users in the future."