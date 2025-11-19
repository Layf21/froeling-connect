# froeling-connect

[![PyPI Version](https://img.shields.io/pypi/v/froeling-connect)](https://pypi.org/project/froeling-connect/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/froeling-connect)
![Development Status: Beta](https://img.shields.io/badge/development%20status-beta-orange)
![Build Status](https://github.com/Layf21/froeling-connect/actions/workflows/ci.yml/badge.svg)
[![License](https://img.shields.io/pypi/l/froeling-connect)](https://github.com/Layf21/froeling-connect/blob/main/LICENSE.txt)
[![CodeFactor](https://www.codefactor.io/repository/github/layf21/froeling-connect/badge/main)](https://www.codefactor.io/repository/github/layf21/froeling-connect/overview/main)

An **unofficial asynchronous Python library** for interacting with the proprietary [Fröling Connect](https://connect-web.froeling.com/) web API.

> ⚠️ This library was primarily tested with the **T4e Boiler**. It may not work reliably with other models.
>
> This project is **not affiliated with Fröling Heizkessel- und Behälterbau Ges.m.b.H.**.<br>
> This library is provided "as is" and comes with **no warranty**.
Use at your own risk. The author is **not responsible for any damages**, including but not limited to equipment damage, fire, water damage, or data loss, resulting from the use of this software.

---

## Features

- Read notifications from Fröling Connect
- Retrieve general information about facilities and components
- Get and set parameters for components (partial support; not all parameters tested)
- Fully asynchronous API calls

---

## Installation

```bash
pip install froeling-connect
```

---

## Terminology

| Name      | Description                                                               | Examples                  |
| --------- | ------------------------------------------------------------------------- | ------------------------- |
| Facility  | A heating installation. One user can manage multiple facilities.          | Wood Chip Boiler T4e      |
| Component | A facility consists of multiple components.                               | Boiler, Heating circuit   |
| Parameter | Components have multiple parameters, including measurements and settings. | Boiler State, Water Temp. |

---

## Usage

Currently, there is no detailed documentation.
You can see a working example [here](https://github.com/Layf21/froeling-connect/blob/main/example.py).

A tiny snippet to showcase some features:
```python
import asyncio
from froeling import Froeling

async def main():
    async with Froeling("username", "password") as api:
        facilities = await api.get_facilities()
        for facility in facilities:
            print(facility)

asyncio.run(main())
```

---

## Notes

* The API is **not public**, so breaking changes on Fröling's end may occur without notice.
* This Project is still in beta; breaking changes are to be expected, though I try to minimize them.
* Contributions and bug reports are welcome.

---

## Contributing

1. Fork the repository
2. Create a feature branch feature/[your-feature], branching off from main
3. Submit a pull request to main with your improvements

This project uses [Hatch](https://hatch.pypa.io/).

```sh
hatch fmt # Run linter and format code
hatch run dev:mypy src # Run mypy type checks
hatch test # Run tests (-a for all python versions)
```

---

## License

[Apache License](https://github.com/Layf21/froeling-connect/blob/main/LICENSE.txt)

---
