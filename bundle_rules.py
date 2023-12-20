"""
Contains all the built-in bundle rules as well as the default one for an unbundled
cable. Bundle(s) usage is to be added to a component's bundle rules
(Note: the overwrite rule is the default rule).
"""


def overwrite(component, value, destination_compartment):
    component.compartments[destination_compartment] = value


def additive(component, value, destination_compartment):
    component.compartments[destination_compartment] += value


def append(component, value, destination_compartment):
    component.compartments[destination_compartment].append(value)
