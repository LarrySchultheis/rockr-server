# rockr-server
## Installing Flask:
### Windows:
```py -3 -m venv .venv```
```.venv\Scripts\activate```
```pip install Flask```

### Mac/Linux:
```python3 -m venv .venv```
```. .venv/bin/activate```
```pip install Flask```

### To run debug mode:
```flask --app rockr run --debug```

### Git Workflow
Branch off of development and merge into development. Team will merge development into main at the end of each sprint (at a minimum).
### Making Contributions (just one way to skin the cat)
1. `git checkout development`
2. `git pull` - make sure local development branch is up to date
3. `git checkout -b ROC-00-name-of-feature` - create feature branch
4. make code changes
5. `git commit -m` - omit the `-m` if you want to write a longer commit message
6. `git push --set-upstream origin ROC-00-name-of-feature`, if development has changed since feature branch was created: `git rebase development`, then rerun the previous command
7. go to github and create a PR!

### Database Migrations For All!
Anytime you make a change to a model, you need to create a migration to persist your change to the db.
1. remember to install from requirements.txt so you have `flaks-migrate`
2. inside your venv run `export FLASK_APP=rockr.py` (you only need to do this the first time)
3. run `flask db migrate`
4. run `flask db upgrade`
 
Bonus reading for the curious: https://flask-migrate.readthedocs.io/en/latest/
