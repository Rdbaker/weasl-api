# Weasl API

## Setup

### Prerequesites

 - Python 3.8
 - PostgreSQL 9.5

### Installation

```bash
pipenv install
. env.sh
. secrets.sh
. setup_db.sh
flask db upgrade
```

## Running the server

```bash
. env.sh
. secrets.sh
flask run
```

## Running the tests

```bash
. env.sh
. secrets.sh
flask test
```
