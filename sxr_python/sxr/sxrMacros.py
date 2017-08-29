import sxrbeamline
import sys
import time
import math


def log_lom(comment=None):
  message = ""
  if comment is not None:
    message = comment + "\n"
  message += sxrbeamline.lom.status()
  sxrbeamline.sxrElog.submit(message)
  pass


