# froeling-connect
An inofficial asynchronous implementation of the proprietary [fröling-connect](https://connect-web.froeling.com/) web API.


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

```py -m pip install froeling-connect```

## Terminology

|Name      | Description                                                               | Examples                  |
|----------|---------------------------------------------------------------------------|---------------------------|
|Facility  | The Heating-Installation. One User can manage multiple Facilities.        | Wood Chip Boiler T4e      |
|Component | A facility consists of multiple Components.                               | Boiler, Heating circuit   |
|Parameter | Components have multiple parameters. These are measurements and settings. | Boiler State, Water Temp. |


## Usage
There is no documentation currently.
Example usage can be found [here](https://github.com/Layf21/froeling-connect/blob/master/example.py)
