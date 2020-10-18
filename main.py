import os
import sys
import pickle
import json

paths = os.environ.get(
    'PYTHONPATH', os.path.abspath('../python_lib') + os.pathsep + os.path.abspath('./libs')).split(os.pathsep)
for p in paths:
    if (p.startswith('.' + os.sep)):
        p = os.path.abspath(p)
    if (p.startswith('~' + os.sep)):
        p = os.path.expanduser(p)
    print(p)
    if (p not in sys.path) and (os.path.exists(p)) and (os.path.isdir(p)):
        print("Adding {} to sys.path.".format(p))
        sys.path.insert(0, p)

import_failures = 0
try:
    from vyperlogix import _utils
except ImportError as ex:
    import_failures += 1
    print(ex)

if (0):
    for f in sys.path:
        print(f)

try:
    from inara import sample as inara_sample
    from inara import scrape_commodities
    from inara import scrape_commodity_data
    from inara import upload_to_google_drive
except ImportError as ex:
    import_failures += 1
    print(ex)

if (import_failures > 0):
    print('Too many import failures. {}'.format(import_failures))
    sys.exit(1)

__scrape_commodities__ = False
__scrape_commodity_data__ = True
__prep_google_creds__ = False
__upload_to_google__ = False

__single_threaded__ = False

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

        target_dirname = './data'
        if (not __single_threaded__):
            import time
            from concurrent import futures as concurrent_futures
            
            __done__ = {'is_done':False}
            def wait_for_output(output_queue, __done__):
                while (1):
                    try:
                        msg = output_queue.get(timeout=5)
                        if (msg):
                            sys.stdout('{}\n'.format(msg))
                        if (__done__.get('is_done', False) and (output_queue.qsize() == 0)):
                            sys.stderr.write('Nothing more to do.\n')
                            break
                    except:
                        __done__['is_done'] = True
                    time.sleep(1)
            
            output = Queue(maxsize = 100)
            items = [wait_for_output, commodities.commodities_by_name.get('Tritium'), commodities.commodities_by_name.get('AgronomicTreatment')]
    
            with concurrent_futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = {executor.submit(scrape_commodity_data, commodity_refid=item, star_system_refid=0, dirname=target_dirname, is_verbose=False, fOut=output) if (not isinstance(item, callable)) else item(output, __done__): item for item in items}
                for future in concurrent_futures.as_completed(futures):
                    try:
                        data = future.result()
                    except Exception as ex:
                        print('Got an exception: %s' % (ex))
                sys.stderr.write('Signal we are done.\n')
                __done__['is_done'] = True
        else:
            import time
            start_time = time.time()
            sys.stdout.write('Single Threaded:\n')
            items = [commodities.commodities_by_name.get('Tritium'), commodities.commodities_by_name.get('AgronomicTreatment')]
            for item in items:
                __commodity_name__ = commodities.commodities_by_value.get(item, 'UNKNWON-COMMODITY')
                fname = 'commodity_{}_report.txt'.format(__commodity_name__)
                fpath = os.sep.join([target_dirname, fname])
                if (not os.path.exists(os.path.dirname(fpath))):
                    os.makedirs(os.path.dirname(fpath))
                with open(fpath, 'w') as ffOut:
                    scrape_commodity_data(commodity_refid=item, star_system_refid=0, dirname=target_dirname, is_verbose=True, fOut=ffOut)
                    ffOut.flush()
            end_time = time.time()
            num_ticks = end_time - start_time
            sys.stdout.write('Run consumed {} ticks.\n'.format(num_ticks))

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
