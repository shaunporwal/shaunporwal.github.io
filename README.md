

#### How to activate renv which handles R & Python dependencies

source ./renv/python/virtualenvs/renv-python-3.11/bin/activate    

#### How to render site locally (with uv)

uv run quarto render

#### How to publish to gh-pages to make changes go live (with uv)

uv run quarto publish gh-pages

#### 241207 - Use venv for virtual env since uv not working for now, set up in env/ in root of repo

source ./env/bin/activate

##### And then can pip install whichever libraries