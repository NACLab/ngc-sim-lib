"""
Contains all the built-in bundle rules as well as the default one for an unbundled
cable. Bundle(s) usage is to be added to a component's bundle rules
(Note: the overwrite rule is the default rule).


Template for bundle rules. The name of the bundle rule should be meaningful to what it does. All bundle rules will
be called with the same three inputs: component, value, and destination_compartment. These are not passed by keyword but
they will always be in the same order. The component is the component that the bundle has as a destination. The value
coming along the connected bundle. The destination_compartment is the compartment the bundle is connected to. Overall
the general usage of bundle rules is to modify the behavior of an input to a compartment, generally they should not
modify anything of the component other than destination compartment and as a warning trying to reference compartments by
name possibly will result in runtime errors as there are not required compartments for bundle rules.


def BUNDLE_RULE_NAME(component, value, destination_compartment):
    ## Logic for processing transmitted value
    ## Syntax for referencing destination compartment -> component.compartments[destination_compartment]

"""
def overwrite(component, value, destination_compartment):
    component.compartments[destination_compartment] = value


def additive(component, value, destination_compartment):
    component.compartments[destination_compartment] += value


def append(component, value, destination_compartment):
    component.compartments[destination_compartment].append(value)
