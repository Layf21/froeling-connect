# froeling-connect

An unofficial asynchronous implementation of the proprietary [fröling-connect](https://connect-web.froeling.com/) web API.

[![PyPi version](https://badgen.net/pypi/v/pip/)](https://pypi.org/project/froeling-connect/)
[![PyPI license](https://img.shields.io/pypi/l/froeling-connect.svg)](https://pypi.org/project/froeling-connect/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/froeling-connect.svg)](https://pypi.org/project/froeling-connect/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Layf21/froeling-connect/master.svg)](https://results.pre-commit.ci/latest/github/Layf21/froeling-connect/master)

## Disclaimer

>This library was only tested with the T4e Boiler, it may not work perfectly for other Machines.
>As this API is not public, there may be breaking changes on the backend.
>### I am not affiliated, associated, authorized, endorsed by, or in any way officially connected with Fröling Heizkessel- und Behälterbau Ges.m.b.H.
>Their official website can be found at https://www.froeling.com.

## Features

* Read notifications
* Get general information about facilities and components managed by the user
* Get and set parameters (not tested for all parameters)

## Installation

```python3 -m pip install froeling-connect```
(May not be up to date, this is my first time using PyPI)

## Terminology

|Name      | Description                                                               | Examples                  |
|----------|---------------------------------------------------------------------------|---------------------------|
|Facility  | The Heating-Installation. One User can manage multiple Facilities.        | Wood Chip Boiler T4e      |
|Component | A facility consists of multiple Components.                               | Boiler, Heating circuit   |
|Parameter | Components have multiple parameters. These are measurements and settings. | Boiler State, Water Temp. |


## Usage

There is no documentation currently.
Example usage can be found [here](https://github.com/Layf21/froeling-connect/blob/master/example.py)

To run it, install [python-dotenv](https://pypi.org/project/python-dotenv/),
and store your credentials in a `.env` file or use:

```shell
USER="foo@example.com" PASSWORD="bar" python3 -m example
```
