
import pathlib
import sys

# NOTE: VN: Since we have installed using `pip install -e .` in the workflow file, we
# might not need to manually add to the path
sys.path.append(str(pathlib.Path(__file__).parent.parent))

# import ngcsimlib

class CompartmentTest:
  
  def test_import(self):
    success = False
    try:
      from ngcsimlib.compartment import Compartment
      success = True
    except:
      success = False
    assert success, "Import failed!"


