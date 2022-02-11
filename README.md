# [Projet CODEV](https://github.com/Louispzt/Projet_codev)

In 2021, the environment is the 4th concern of the French. For example, electrical energy alone represents 41% of CO2 emissions worldwide (9% in France). Vital for the whole population of the population, energy is obtained and produced in different ways across the globe.

The consumption of the French, as well as the production of this energy produces a very large amount of raw data that can be raw data that can be found and/or consumed (OpenData) on the Internet.

However, without processing and personalized display, this data has little value. In order increase its value and bring the information it carries to the French citizen, propose a solution that recovers, transforms and displays it in real time.

The project
Imagining an application
Presentation of energy data

- sources to choose from ([examples]{https://github.com/tmrowco/electricitymap-contrib/blob/master/DATA_SOURCES.md})

## Constraints

- Data updated in real time / updated regularly
- User management / favorites / personalized / customizable experience
- Hosted in the cloud

## Conceptualize and build the application

Build the Backend and Frontend parts
Demonstration

# Installation

### Use Virtualenv

This repo uses virtualenv

Installation of the dependencies required for the project:

```bash
# activation of the virtual environment
... $> source .venv/bin/activate

# installation of dependencies (only after having activated the virtual environment!)
(.venv) ... $> pip3 install -r requirements.txt
```

Don't forget to add a SECRET_KEY:

```bash
# Create a .env file
(.venv) ... $> cp .env.example .env
# You can create a SECRET_KEY with
(.venv) ... $> openssl rand -hex 32
# Add the SECRET_KEY
(.venv) ... $> nano .env
```

Then, to launch the bot simply type:

```bash
# start the API
(.venv) ... $> python3 main.py
```
