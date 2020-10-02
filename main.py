import os
import sys
print("PYTHONPATH = {}".format(os.environ['PYTHONPATH']))

paths = os.environ['PYTHONPATH'].split(os.pathsep)
for p in paths:
    if (p not in sys.path):
        print("Adding {} to sys.path.".format(p))
        sys.path.insert(0, p)

from vyperlogix import _utils

for f in sys.path:
    print(f)

from inara import sample as inara_sample
from inara import scrape_commodities
from inara import scrape_commodity_data

__scrape_commodities__ = False

if (__name__ == '__main__'):
    # float(sys.version_info.major)+(float(sys.version_info.minor)/10)+(float(sys.version_info.micro)/100)
    py_version = _utils.getVersionFloat()
    if (py_version < 3.9):
        print('ERROR: Requires Python 3.9.x rather than {}. Please use the correct Python version.'.format(
            py_version))

    if (__scrape_commodities__):
        scrape_commodities()
        from commodities import Commodities
        from commodities import all_commodities
        from commodities import commodities
    scrape_commodity_data()