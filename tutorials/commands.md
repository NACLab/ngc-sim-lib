# Commands

## Overview
Commands are one of the central pillars of ngclib. They provide the instructions
and logic for what each component should be doing at any given time. They also
are the normal way that an outside user would interact with models. Commands 
live in the controller and are generally made with the `add_command` method.

## Abstract Command
Contained inside ngclib is an abstract class for every command included in 
ngclib. It is recommended that custom commands are built using this base 
class but there is nothing enforcing this inside of ngclib.

At its base the abstract command forces two things, firstly the constructor 
for the base class requires a list of components, and a list of attributes 
each component should have. Secondly all commands must implement their 
`__call__` command, taking in only `*args` and `**kwargs`.

## Constructing Commands
Commonly commands will need to have values passed into them to control their 
internal behavior, such as a value to clamp, or a flag for freezing weights. 
To do this we introduce the concept of binding keywords to commands. 
Specifically commands will take strings in during their construction and then 
look for those strings when called inside the list of keyword arguments to 
get their arguments.

## Calling Commands
When commands are called they will take in only `*args` and `**kwargs`. 
While custom commands can break this by adding in additional arguments 
without a problem it is not recommended to this as then multiple instances 
of a command with different parameters will use the same keyword for their 
call.

## Creating Custom Commands
It is recommended that all custom commands inherent from the base class 
provided in ngclib. This provides a good base point for every component. 
The normal paradigm that is followed by each provided command is that a command 
will call the same function with the same parameters on each component provided 
to the command. It is also expected that there is error handling in the 
constructor to catch as many run time errors as possible. The base class 
provides a list to check required calls such as `clamp` or `evolve`.

It is important to note that if commands are going to be constructed via a 
controller they should have keyword arguments with default values that 
error on bad input instead of positional arguments.

## Example Command (Clamp)
```python
from ngclib.commands.command import Command
from ngclib.utils import extract_args

class Clamp(Command):
    def __init__(self, components=None, compartment=None, clamp_name=None, **kwargs):
        super().__init__(components=components, required_calls=['clamp'])
        if compartment is None:
            raise RuntimeError("A clamp command requires a \'compartment\' to clamp to for construction")
        if clamp_name is None:
            raise RuntimeError("A clamp command requires a \'clamp_name\' to bind to for construction")
    
        self.clamp_name = clamp_name
        self.compartment = compartment

    def __call__(self, *args, **kwargs):
        try:
            vals = extract_args([self.clamp_name], *args, **kwargs)
        except RuntimeError:
            raise RuntimeError("Clamp, " + str(self.clamp_name) + " is missing from keyword arguments or a positional "
                                                                  "arguments can be provided")

        for component in self.components:
            self.components[component].clamp(self.compartment, vals[self.clamp_name])
```

## Custom Command Template
```python
from ngclib.commands.command import Command
from ngclib.utils import extract_args

class CustomCommand(Command):
    def __init__(self, components=None, BINDING_VALUE=None, ADDITIONAL_INPUT=None, 
                 **kwargs):
        super().__init__(components=components, required_calls=['CUSTOM_CALL'])
        # Make sure additional input is passed in
        if ADDITIONAL_INPUT is None:
            raise RuntimeError("A custom command requires a \'ADDITIONAL_INPUT\' for construction")
        
        # Make sure command is bound to a value
        if BINDING_VALUE is None:
            raise RuntimeError("A custom command requires a \'BINDING_VALUE\' to bind to for construction")
    
        self.BOUND_VALUE = BINDING_VALUE
        self.ADDITION_VALUE = ADDITIONAL_INPUT

    def __call__(self, *args, **kwargs):
        # Extract the bound value from the arguments
        try:
            vals = extract_args([self.BOUND_VALUE], *args, **kwargs)
        except RuntimeError:
            raise RuntimeError("Custom, " + str(self.BOUND_VALUE) + " is missing from keyword arguments or a positional "
                                                                  "arguments can be provided")
        
        #Use extracted value to call a method on each component
        for component in self.components:
            self.components[component].CUSTOM_CALL(self.ADDITION_VALUE, vals[self.BOUND_VALUE])
```

## Notes
All components added to commands must have a `name` attribute and the word 
`name` is automatically appended to any provided list of required attributes 
to the base class constructor. 

As all built in commands use `extract_args` when called with a controller via
`myController.COMMAND(ARGUMENT)` there is no need to use keywords as it will 
use `args` if there are no keyword arguments. (Keywords will still work)

When commands are constructed via a controller they are also provided the 
keyword arguments `controller`, and `command_name`. It is not recommended to 
use these for logic just for error messages, unless really needed to achieve 
the desired functionality.