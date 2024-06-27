
import pathlib
import sys
from functools import partial as bind

# NOTE: VN: Since we have installed using `pip install -e .` in the workflow file, we
# might not need to manually add to the path
sys.path.append(str(pathlib.Path(__file__).parent.parent))

import ngcsimlib

def test_import():
  success = False
  try:
    from ngcsimlib.compartment import Compartment
    success = True
  except:
    success = False
  assert success, "Import failed!"


