# Parent-Portal

## What is this?

KMRPP (**K**A**M**A**R** **P**arent **P**ortal) is a cli tool to help get data from your KAMAR* parent portal in the terminal. This tool allows you to view your timetable in the terminal.

*KAMAR Parent Portal is a brand of portal used a lot in new zealand schools.

---
## Usage

First install the tool with pip:
```
pip install kmrpp
```

Next check if the tool is installed by typing `kmr` in terminal.  

You should get something like: 

![](https://raw.githubusercontent.com/st22209/Parent-Portal/main/assets/installed_example.jpg)

If that didn't work try: `python3 -m kmrpp` or `python -m kmrpp`: 

![](https://raw.githubusercontent.com/st22209/Parent-Portal/main/assets/installed_example2.jpg)

If you saw any of those above 2 images the tool has successfull been installed (If not skill issue tbh).  
Now that you have it installed use `kmr --help` (or `python -m kmrpp --help`) to list commands.

For the cli utility to work you must be logged in first so i recommend doing that:

### Login

To login to the api use login command:
```
kmr login --username <Your Username>
```
(you can also use `kmr l`)

It should prompt you for your password and once you enter it you should be logged in.

### Get your timetable

To get your timetable use that timetable command:
```
kmr timetable --week <Week>
```
(Alias for timetable command is `kmr tt`)

**Tip:** If you want this weeks timetable type `kmr timetable` without giving the week option. It will then try to get the current weeks timetable.

---

## Example Using The CLI

![](https://raw.githubusercontent.com/st22209/Parent-Portal/main/assets/timetable.jpg)

(This may look different if you are using a newer version)

---

## Example using it as a package

While the CLI is the primary use of this project, if you want you can import it into you python code and use it directly.  

Here is an example:
```py
from rich import print # for pretty printing
from kmrpp import ParentPortal, Week, parse_timetable

USERNAME = "person123"
PASSWORD = "password456"

# create parent portal object and login
portal = ParentPortal(USERNAME, PASSWORD)

# fetch data from api (or cache)
timetable_data = portal.timetable()  # example using cache
period_data = portal.periods(use_cache=False)  # not using cache

# this is a list of Week objects
parsed_tt: list[Week] = parse_timetable(timetable_data, period_data)

# get week 3's data
week3_data = parsed_tt[2]
print(week3_data.days["Monday"])
```

**Note: This tool is not affiliated with KAMAR**