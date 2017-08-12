# -*- coding: utf-8 -*-

"""
Programmers: DGP

Purpose: Making the code more readable, eliminating in the initialization
         the creation of default parameters.

Structure class makes simple to create classes with
attributes, which are set to some predefined value. This avoids code
repetition, just defined an attribute _fields with the preassigned values.


"""


from inspect import Parameter, Signature


def make_signature(names):
    return Signature(
        Parameter(name[0], Parameter.POSITIONAL_OR_KEYWORD, default=name[1])
        if isinstance(name, tuple) else
        Parameter(name, Parameter.POSITIONAL_OR_KEYWORD)
        for name in names
    )


class StructMeta(type):
    def __new__(cls, name, bases, clsdict):
        clsobj = super().__new__(cls, name, bases, clsdict)
        sig = make_signature(clsobj._fields)
        setattr(clsobj, '__signature__', sig)
        return clsobj


class Structure(metaclass=StructMeta):
    '''
    Structure class. It has only a constuctor
    which sets the attributes to the correct values and
    a list of functions to process the correct initializations.
    '''
    _fields = []
    _proccessing = []

    def __init__(self, *args, **kwargs):
        # We take the names of the args
        dict_names = dict()
        for pos, name in enumerate(self._fields[:len(args)]):
            if isinstance(name, str):
                dict_names[name] = args[pos]
            else:
                dict_names[name[0]] = args[pos]
        dict_names.update(kwargs)
        # We check for the positional elements that are not defined.
        for f in self._fields[len(args):]:
            if isinstance(f, tuple):
                # we allow that some attributes to be functions
                if callable(f[1]):
                    # Here, we evaluate with the arguments in kwargs
                    # If there are not present, we use the ones defined in
                    # _fields
                    parameters = [kwargs[n] if n in kwargs else dict_names[n]
                                  for n in f[2]]
                    kwargs[f[0]] = f[1](*parameters)
                elif f[0] not in kwargs:
                    kwargs[f[0]] = f[1]
        bound = self.__signature__.bind(*args, **kwargs)
        for name, val in bound.arguments.items():
            setattr(self, name, val)
        for val in self._proccessing:
            val(self)
