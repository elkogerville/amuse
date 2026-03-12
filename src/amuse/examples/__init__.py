""" Forward examples

This does not use amuse.support.helpers.load_symbol, because we don't have an interface.py
and because we want to have different error messages. We're not loading a code, in
short.
"""
from importlib import import_module
from os import environ


def _load_symbol(symbol):
    try:
        module = import_module("amuse_examples")
    except ImportError:
        msg = f"Error: The examples are not installed."
        if "CONDA_PREFIX" in environ:
            env = environ["CONDA_DEFAULT_ENV"]
            msg += (
                    " To install the examples go to the terminal, make sure that"
                    f" the '{env}' conda environment is active and that you are in the"
                    " amuse source directory, then install them using './setup"
                    " install amuse-examples' and restart your script or reload the"
                    " kernel.")

        if "VIRTUAL_ENV" in environ:
            env = environ["VIRTUAL_ENV"]
            msg += (
                    " To install the examples, go to the terminal, make sure that"
                    f" the '{env}' virtual environment is active and that you are in"
                    " the amuse source directory, then install the code using './setup"
                    " install amuse-examples' and restart your script or reload the"
                    " kernel.")
        raise ImportError(msg) from None

    try:
        return vars(module)[symbol]
    except KeyError:
        raise ImportError(
                f"cannot import '{symbol}' from 'amuse_examples'"
                ) from None


get = _load_symbol("get")
to_cell = _load_symbol("to_cell")
show = _load_symbol("show")
run = _load_symbol("run")
shell_is_interactive = _load_symbol("shell_is_interactive")
