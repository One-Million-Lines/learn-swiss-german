

cd _ops/pip/
pip-compile requirements.in
pip install -r requirements.txt



# check what is outdated
pip list --oudated


# upgrade 
pip-compile --upgrade