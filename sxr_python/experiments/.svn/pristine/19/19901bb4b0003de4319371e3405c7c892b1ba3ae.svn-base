from blutil import config
from blutil import printnow
from importlib import import_module


def load_exp(experiment=None):
  if experiment is None:
    experiment = config.Elog.experiment['name']
  currExp = import_module('experiments.%s'%experiment)
  user = currExp.USER()
  return user

def load_exp_macros(experiment=None):
  if experiment is None:
    experiment = config.Elog.experiment['name']
  macro_mod = import_module('experiments.%s_macros'%experiment)
  user_macros = macro_mod.macros()
  return user_macros
