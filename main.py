import os
import sys
import pickle
import json
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
from inara import upload_to_google_drive

__scrape_commodities__ = False
__scrape_commodity_data__ = True
__prep_google_creds__ = False
__upload_to_google__ = False

if (__name__ == '__main__'):
    # float(sys.version_info.major)+(float(sys.version_info.minor)/10)+(float(sys.version_info.micro)/100)
    py_version = _utils.getVersionFloat()
    if (py_version < 3.8) or (py_version > 3.9):
        print('ERROR: Requires Python 3.8.x rather than {}. Please use the correct Python version.'.format(
            py_version))
        sys.exit(-1)

    if (__scrape_commodities__):
        scrape_commodities()
        from commodities import Commodities
        from commodities import all_commodities
        from commodities import commodities
    if (__scrape_commodity_data__):
        from queue import Queue
        import commodities

        if (0):
            import time
            from concurrent import futures as concurrent_futures
            
            __done__ = False
            def wait_for_output(output_queue):
                while (1):
                    try:
                        msg = output_queue.get(timeout=5)
                        if (__done__ and (output_queue.qsize() == 0)):
                            sys.stderr.write('Nothing more to do.\n')
                            break
                    except:
                        __done__ = True
                    time.sleep(1)
            
            output = Queue(maxsize = 100)
            items = [commodities.commodities_by_name.get('Tritium'), commodities.commodities_by_name.get('AgronomicTreatment')]
    
            with concurrent_futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(scrape_commodity_data, commodity_refid=item, star_system_refid=0, dirname='./data', is_verbose=False, fOut=output): item for item in items}
                for future in concurrent_futures.as_completed(futures):
                    try:
                        data = future.result()
                    except Exception as ex:
                        print('Got an exception: %s' % (ex))
                sys.stderr.write('Signal we are done.\n')
                __done__ = True
        else:
            items = [commodities.commodities_by_name.get('Tritium'), commodities.commodities_by_name.get('AgronomicTreatment')]
            for item in items:
                scrape_commodity_data(commodity_refid=item, star_system_refid=0, dirname='./data', is_verbose=False, fOut=sys.stdout)

    if (__prep_google_creds__):
        fpath1 = os.path.abspath('./token.pickle')
        fpath2 = os.path.abspath('./client_secrets.json')
        has_file1 = (os.path.exists(fpath1)) and (os.path.isfile(fpath1))
        has_file2 = (os.path.exists(fpath2)) and (os.path.isfile(fpath2))
        if (has_file1):
            if (not has_file2):
                with open(fpath1, 'rb') as token:
                    creds = pickle.load(token)
                    my_creds = json.loads(creds.to_json(strip=None))
                    my_creds["redirect_uris"] = ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
                    my_creds["auth_uri"] = "https://accounts.google.com/o/oauth2/auth"
                    my_creds = {"installed": my_creds}
                    with open(fpath2, 'w') as secrets:
                        secrets.write(json.dumps(my_creds))
        else:
            print("ERROR: Missing the creds in {}.".format(fpath1))
            sys.exit(-1)
                
    if (__upload_to_google__):
        fpath = os.path.abspath('./data')
        files = [os.sep.join([fpath, f]) for f in os.listdir(fpath)]
        for f in files:
            upload_to_google_drive(f)
