# The modules.json file

## Basic Usage:

The basic usage for the `modules.json` file is to provide a straight forward 
method for the imports of arbitrary classes and methods without needing to 
register them before use. The primary use for these is when adding components
and commands to controller objects. If there is a need to use the imported
modules outside of these cases, use `ngclib.utils.load_attribute` and the loaded
attribute will be returned.

By default, ngclib looks for `json_files/modules.json` in your project path. 
However, this can be changed with the `--modules` flag. In the event that this 
file is missing, ngclib will not break but its ability to import and create 
parts of the model will be hindered. It is highly recommended to set up the 
`modules.json` file at the start of the project. There is a schema file named 
`modules.shema` that can be referenced and use to verify that custom modules 
files are in the correct format for use. 

## Motivation

The motivation behind the use of `modules.json` vs the registering all the 
various parts of the model at the top of the file was reusability. When all the 
parts have to be registered/imported at the top of a trail file, the creation of 
additional trial files will lead to code duplication. Obviously one solution to 
this code duplication is to extract it into a file and then import and run that 
file at the top of each trial. This is almost what was done in ngclib, but we 
also had the goal of allowing users to alias components, and then swap out their 
source with ease. To do this we moved to the use of a json file that fulfills 
our needs.

## Structure
A complete schema for the modules file can be found in `modules.schema`

The general structure of the modules file can be though of as a transformation
of python import statements to json objects. Take the following example
```python
from ngclib.commands import AdvanceState as advance
```
In this statement we are importing a command from ngclib and aliasing it to the
word "advance". Now we will transform this into json for the modules file. First 
we take the top level module we are importing from, in this case 
`ngclib.commands`, this the absolute path to the location of this module. Next 
we look at the name of what we are importing here `AdvanceState`. Finally, we 
look at the keyword being this import is being assigned to `advance`. We then 
take these three parts and combing them into the following json object.
```json
  {
    "absolute_path": "ngclib.commands",
    "attributes": [
      {
        "name": "AdvanceState",
        "keywords": ["advance"]
      }
    ]
  }
```
Now there are a few additional things that this json formulation of an import
allows us to do. Primarily it allows for multiple keywords for a single import
to be defined. This if we wanted to use `advance` and `adv` all we would do is
change the keyword line to `"keywords": ["advance", "adv"]`. Also, we are able
to specify more than one attribute to import from a single top level module
such as also importing the evolve command.
```json
  {
    "absolute_path": "ngclib.commands",
    "attributes": [
      {
        "name": "AdvanceState",
        "keywords": ["advance", "adv"]
      },
      {
        "name": "Evolve"
      }
    ]
  }
```
Now you will notice that when importing the evolve attribute no keywords were
given. This means that in order to add an evolve command to the controller the
whole name will need to be given. There is one caveat to this though, it is 
case-insensitive by default, meaning that both `Evolve` and `evolve` are valid
ways to using this import.

## Example Transformations

### Case 1
Python:
```python
from ngclib.commands import AdvanceState as advance, Evolve, multiclamp as mClamp
```
Json:
```json
[
  {
    "absolute_path": "ngclib.commands",
    "attributes": [
      {
        "name": "AdvanceState",
        "keywords": ["advance"]
      },
      {
        "name": "Evolve"
      },
      {
        "name": "Multiclamp",
        "keywords": "mClamp"
      }
    ]
  }
]
```

### Case 2
Python
```python
from ngclib.commands import AdvanceState as advance
from ngclib.bundle_rules import additive as add, overwrite
```

Json
```json
[
  {
    "absolute_path": "ngclib.commands",
    "attributes": [
      {
        "name": "AdvanceState",
        "keywords": ["advance"]
      }
    ]
  },
  {
    "absolute_path": "ngclib.bundle_rules",
    "attributes": [
      {
        "name": "additive",
        "keywords": ["add"]
      },
      {
        "name": "overwrite"
      }
    ]
  }
]
```
