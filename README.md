

#### How to activate renv which handles R & Python dependencies

source ./renv/python/virtualenvs/renv-python-3.11/bin/activate    

#### 241207 - Use venv for virtual env since uv & renv not working for now, set up in env/ in root of repo

source ./env/bin/activate

#### How to render site locally

quarto render

#### How to publish to gh-pages to make changes go live (with uv)

quarto publish gh-pages

##### And then can pip install whichever Python libraries 