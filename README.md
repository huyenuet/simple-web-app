# Set up a virtual environment
It’s good practice to create isolated Python environments for your Python project. To ensure that you have virtualenv installed, run the command below:

`pip install virtualenv`

Now, create a new directory called server-side-rendering-with-fastapi. Navigate to it and use the command below to create a virtual environment:

`python3 -m venv env`

To activate the virtual environment we just created, run the command below:

`source env/bin/activate`

# Install dependencies
Now, let’s install the necessary packages for our project. We will use Uvicorn as our ASGI development server, Jinja2 as our template engine, and python-multipart to receive form fields from the client:
`pip install fastapi uvicorn jinja2 python-multipart`

## Install SQLAlchemy
`pip install sqlalchemy`

## install mysql
`pip install mysql-connector-python`
