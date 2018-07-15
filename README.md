# Noath API

## Setup

### Prerequesites

 - Python 3.6
 - PostgreSQL 9.5

### Installation

```bash
pip install -r requirements/dev.txt
. env.sh
. secrets.sh
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
