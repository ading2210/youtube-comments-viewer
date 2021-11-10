import os

try:
  import flask, pyyoutube, dateutil
except ModuleNotFoundError:
  print("Installing packages...")
  os.system("pip3 install flask python-youtube python-dateutil")
  os.system("clear")