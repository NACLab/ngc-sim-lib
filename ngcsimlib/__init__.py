from ngcsimlib._src.component import Component as Component
from ngcsimlib._src.process.methodProcess import MethodProcess
from ngcsimlib._src.process.jointProcess import JointProcess
from ngcsimlib._src.deprecators import deprecated, deprecate_args
from ngcsimlib._src.configManager import init_config
from ngcsimlib._src.configManager import get_config, provide_namespace
import sys, argparse, os, json

########################################################################################################################
if sys.version_info >= (3, 8): ## for new versions of python/ngc-learn
    from importlib.metadata import version, distributions, PackageNotFoundError
else: ## for older versions of python before 3.8
    from importlib_metadata import version, distributions, PackageNotFoundError

## Following obtains ngc-learn's version
from importlib.metadata import version
__version__ = version("ngcsimlib")

## these two lines below are deprecated if using newer python(s) (had to do this for ngc-learn)
# from pkg_resources import get_distribution
# __version__ = get_distribution('ngcsimlib').version
########################################################################################################################

def configure():
    parser = argparse.ArgumentParser(description='Build and run a model using ngclearn')
    parser.add_argument("--config", type=str, help='location of config.json file')

    ## ngc-sim-lib only cares about --config argument
    args, unknown = parser.parse_known_args()  # args = parser.parse_args()
    try:
        config_path = args.config
    except:
        config_path = None

    if config_path is None:
        config_path = "json_files/config.json"

    if not os.path.isfile(config_path):
        # warn("Missing configuration file. Attempted to locate file at \"" + str(config_path) +
        #               "\". Default Config will be used. "
        #               "\nSee https://ngc-learn.readthedocs.io/en/latest/tutorials/model_basics/configuration.html for "
        #               "additional information")
        return

    init_config(config_path)
