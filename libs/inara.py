__copyright__ = """\
(c). Copyright 2008-2020, Vyper Logix Corp., All Rights Reserved.

Published under Creative Commons License 
(http://creativecommons.org/licenses/by-nc/3.0/) 
restricted to non-commercial educational use only., 

http://www.VyperLogix.com for details

THE AUTHOR VYPER LOGIX CORP DISCLAIMS ALL WARRANTIES WITH REGARD TO
THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS, IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL,
INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING
FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION
WITH THE USE OR PERFORMANCE OF THIS SOFTWARE !

USE AT YOUR OWN RISK.
"""
import os
import sys
import math

class CommodityError(Exception):
    pass

class CommodityValueError(Exception):
    pass

def sample():
    """
    $apitestdata = array();   // your data should be there
    $jsondata = json_encode($apitestdata);
    $url = "https://inara.cz/inapi/v1/";
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array("Content-Type: application/json"));
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $jsondata);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    $response = curl_exec($ch);
    curl_close($ch);
    $result = json_decode($response, true);   // process the result as you wish
    """
    import requests
    import simplejson

    apidata = """
    {
        "header": {
            "appName": "TheCappySmackApp",
            "appVersion": "0.1",
            "isDeveloped": true,
            "APIkey": "7uhx0rc25zocwco0w8w48ockw0ogcswoscwo4gk",
            "commanderName": "CappySmack",
            "commanderFrontierID": "3478314"
        },
        "events": [
            {
                "eventName": "getCommanderProfile",
                "eventTimestamp": "2017-05-02T17:30:49Z",
                "eventData": {
                    "searchName": "CappySmack"
                }
            }
        ]
    }
"""
    apidata = ''.join([ll for ll in [str(l).strip() for l in apidata.split('\n')] if (len(ll) > 0)])
    payload_data =  simplejson.loads(apidata)
    payload =  simplejson.dumps(payload_data)
    url = "https://inara.cz/inapi/v1/"

    headers = {
        'user-agent': 'my-app/0.0.1',
        'Content-Type': 'application/json'
    }
    r = requests.post(url, data=payload, headers=headers)
    if (r.ok):
        response = r.json()
        print(response)

    #$result = json_decode($response, true);   // process the result as you wish


def scrape_commodities():
    import os
    import requests

    from vyperlogix import enum

    from bs4 import BeautifulSoup

    from io import StringIO

    commodities = {}

    __tritium__ = 'Tritium'

    commodities_url1 = "https://inara.cz/galaxy-commodities/"

    r = requests.get(commodities_url1)
    if (r.ok):
        soup = BeautifulSoup(r.content, 'html.parser')
        divs = soup.findAll(name='div', attrs={'class':"maincontentcontainer"})
        selects = soup.findAll(name='select', attrs={'name':'searchcommodity'})
        for sel in selects:
            for child in sel.children:
                if (child.name.lower() == 'option'):
                    if (child.getText() not in commodities.keys()):
                        commodities[child.getText()] = child.attrs.get('value', None)
                    print('{} --> {}'.format(child.getText(), child.attrs))
        if (__tritium__ not in commodities.keys()):
            raise(CommodityError, 'Cannot find {}.'.format(__tritium__))
        trit = commodities.get(__tritium__, None)
        if (not trit):
            raise(CommodityValueErrorError, 'Cannot find value for {}.'.format(__tritium__))
        fname = os.path.abspath('./libs/commodities.py')
        with open(fname, 'w') as ffOut:
            fOut = StringIO()
            fOut.write('from vyperlogix import enum\n')
            fOut.write('class Commodities(enum.Enum.Enum):\n')
            for k,v in commodities.items():
                fOut.write('{}{}={}\n'.format(' '*4,''.join(''.join(''.join(k.split()).split('-')).split('.')),v))
            fOut.write('')
            fOut.write('')
            fOut.write("is_normalized_key = lambda key:(not str(key).startswith('__')) and (not str(key).endswith('__'))\n")
            fOut.write("all_commodities = [k for k in Commodities.__dict__.keys() if (is_normalized_key(k))]\n")
            fOut.write("commodities = dict([tuple([k,v]) for k,v in Commodities.__dict__.items() if (is_normalized_key(k))])\n")
            fOut.write('')
            fOut.flush()
            ffOut.writelines(fOut.getvalue())
            fOut.close()
    else:
        print('WARNING: Problem with {} {}.'.format(commodities_url1, r.status_code))


def upload_to_google_drive(fname):
    import os
    from vyperlogix import _utils
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
    
    gauth = GoogleAuth()
    my_creds_fpath = os.path.abspath('./mycreds.txt')
    if (not os.path.exists(my_creds_fpath)) or (not os.path.isfile(my_creds_fpath)):
        gauth.LocalWebserverAuth() # bootstrap to achieve the desired goal.
        gauth.SaveCredentialsFile(my_creds_fpath)
    else:
        gauth.LoadCredentialsFile(my_creds_fpath)
    
    drive = GoogleDrive(gauth)    

    target_drive_folder = '@data'
    try:
        folders = drive.ListFile({'q': " title='{}' ".format(target_drive_folder)}).GetList()
    except Exception as ex:
        print('WARNING: {}.'.format(ex))
        folders = []

    for folder in folders:
        if folder['title'] == target_drive_folder:
            target_filename = '{}_{}'.format(os.path.basename(fname), _utils.timeStampForFileName())
            print('{} {} --> {}'.format(folder.get('id'), folder.get('title'), target_filename))
            file2 = drive.CreateFile({'parents': [{'id': folder['id']}], 'title': target_filename})
            file2.SetContentFile(fname)
            file2.Upload()    
    print('\n')
        
        
def scrape_commodity_data(commodity_refid=10269, star_system_refid=0, dirname='./data', is_verbose=False, fOut=sys.stdout):
    """
    fOut can be sys.stdout or a Queue to allow for background processing.
    """
    import requests

    from vyperlogix import _utils
    
    import commodities

    from bs4 import BeautifulSoup

    __location__ = 'Location'

    __special_cols__ = [__location__, 'Buy price', 'Sell price', 'QTY', 'St dist', 'Distance']
    
    normalize_key = lambda k:'{}{}'.format('_'.join([t for t in str(k).split() if (len(t) > 0)]),'_value')
    
    __commodity_name__ = commodities.commodities_by_value.get(commodity_refid, None)
    if (__commodity_name__ is None) or (not isinstance(__commodity_name__, str)):
        raise(CommodityValueError, 'WARNING: Cannot resolve {} to a valid Commodity Name.'.format(commodity_refid))
    
    #__tritium__ = 'Tritium'

    #tritium_url = "https://inara.cz/ajaxaction.php?act=goodsdata&refname=buymin&refid=10269&refid2=367"     # refid is the commodity, refid2 is the star system.
    #tritium_url2 = "https://inara.cz/ajaxaction.php?act=goodsdata&refname=buymin&refid=10269&refid2=18698"
    #tritium_url3 = "https://inara.cz/ajaxaction.php?act=goodsdata&refname=sellmax&refid=10269&refid2=18698"

    #commodities_url1 = "https://inara.cz/galaxy-commodity/10269/"
    commodities_buymin_url = "https://inara.cz/ajaxaction.php?act=goodsdata&refname=buymin&refid={}&refid2={}".format(commodity_refid, star_system_refid)
    commodities_sellmax_url = "https://inara.cz/ajaxaction.php?act=goodsdata&refname=sellmax&refid={}&refid2={}".format(commodity_refid, star_system_refid)


    def format_header(row, use_keys=True):
        formatted_header = []
        try:
            subj = row.keys() if (use_keys) else row.values()
            fmt = ['{}'.format(item) for item in subj]
            for item in fmt:
                formatted_header.append(item)
            formatted_header = '\t'.join(formatted_header).strip()+'\n'
        except Exception as ex:
            formatted_header = '-- INVALID --'
        return formatted_header


    def print_data(the_data, verbose=False):
        from io import StringIO

        fOut = StringIO()
        fOut.write('BEGIN:\n')
        has_header = False
        try:
            for row in the_data:
                if (len(row.keys()) > 0):
                    if (not has_header):
                        fOut.write(format_header(row, use_keys=True))
                        has_header = True
                    fOut.write(format_header(row, use_keys=False))
        except Exception as ex:
            print(ex)
        fOut.flush()
        lines = fOut.getvalue().split('\n')
        fOut.write('END!!!\n')
        for l in lines:
            if (verbose):
                print(l)
        fOut.close()
        
        
    def export_as_csv_file(the_headers, the_data, dirname, basefilename, verbose=False):
        import os
        import csv
        try:
            fpath = os.path.abspath(dirname)
            if (not os.path.isdir(fpath)):
                os.mkdir(fpath)
            fname = os.path.abspath(os.path.join(fpath, basefilename))
            with open(fname,mode='w',encoding='utf8',newline='') as output_to_csv:
                dict_csv_writer = csv.DictWriter(output_to_csv, fieldnames=the_headers,dialect='excel')
                dict_csv_writer.writeheader()
                dict_csv_writer.writerows(the_data)
            if (verbose):
                print('\nData exported to {} succesfully and sample data'.format(fname))
        except IOError as io:
            print('\n',io)
        
        
    def harmonic_averages(dataFrame, col_name, harmonic=2, qty_col_name=None, min_qty=1000, lower_bound=None, upper_bound=None):
        """
        This could be used to produce a set of bands of selectioned regions to help determine regions of interest.
        """
        subDataFrame = dataFrame
        new_lower_bound = dataFrame[col_name].min()
        new_upper_bound = dataFrame[col_name].max()
        if (lower_bound):
            subDataFrame = subDataFrame[col_name] >= lower_bound
        if (upper_bound):
            subDataFrame = subDataFrame[col_name] <= upper_bound
        if (qty_col_name):
            subDataFrame = subDataFrame[(subDataFrame[qty_col_name] >= min_qty)]
        while (True):
            count = subDataFrame[col_name].count()
            sample_mean = subDataFrame[col_name].mean()
            subDataFrame = subDataFrame[subDataFrame[col_name] < sample_mean]
            new_count = subDataFrame[col_name].count()
            if (new_count < (count / harmonic)):
                new_lower_bound = subDataFrame[col_name].min()
                new_upper_bound = subDataFrame[col_name].max()
                break
        return dataFrame[(dataFrame[col_name] >= new_lower_bound) & (dataFrame[col_name] <= new_upper_bound)]


    def fetch_data_from(url, dirname=None, filename=None, is_verbose=False, is_debugging=False, is_uploading=False, filter_keys_for_callback=[], callback=None):
        the_headers = set()
        the_results = []
        r = requests.get(url)
        if (r.ok):
            soup = BeautifulSoup(r.content, 'html.parser')
            tables = soup.findAll(name='table', attrs={'class':"tablesorter"})
            for table in tables:
                headers = [header.text for header in table.find_all('th')]
                results = [{headers[i]: cell for i, cell in enumerate(row.find_all('td'))}
                           for row in table.find_all('tr')]
                for result in results:
                    if (len(result.keys()) > 0):
                        row = {}
                        for k,v in result.items():
                            items_in_row = []
                            try:
                                for item in [c for c in v.children]:
                                    try:
                                        items_in_row.append(item.text)
                                    except Exception as ex:
                                        items_in_row.append(str(item))
                                row[k] = ''.join(items_in_row)
                            except Exception as ex:
                                print(ex)
                        the_results.append(row)
                break
    
            # filter the buy price to ensure the value is float
            new_results = []
            for row in the_results:
                use_the_row = True
                for k in filter_keys_for_callback:
                    fuzzy_row_keys = dict([tuple([kk.lower(),kk]) for kk in row.keys()])
                    if (k is None):
                        continue
                    kk = fuzzy_row_keys.get(k.lower(), None)
                    if (kk):
                        k = kk
                        did_callback_happen = False
                        if (not _utils.is_floating_or_numeric_digits(row.get(k, 0.0))):
                            new_key = normalize_key(k)
                            try:
                                if (callable is not None) and (callable(callback)):
                                    new_key, new_value = callback(k, row.get(k), filter_keys_for_callback)
                                    did_callback_happen = True
                            except Exception as ex:
                                print(ex)
                        if (not did_callback_happen):
                            new_value = row.get(k, 0.0)
                            if (not isinstance(new_value, float)):
                                try:
                                    new_value = ''.join([c for c in new_value if (_utils.is_floating_or_numeric_digit(c))]).replace('...', '').replace('..', '')
                                    new_value = float(new_value) if (_utils.is_floating_or_numeric_digits(new_value)) else 0.0
                                except Exception as ex:
                                    sys.stderr.write('{}\n'.format(ex))
                        if ((new_key is not None) and (new_value is not None)):
                            row[new_key] = new_value
                            if (is_debugging):
                                print('{} -> {} --> {} -> {}'.format(k, row.get(k, 0.0), new_key, row.get(new_key, 0.0)))
                        else:
                            use_the_row = False
                            break
                if (use_the_row):
                    new_results.append(row)
    
            the_results = new_results
            if (is_verbose):
                print_data(the_results, verbose=is_verbose)        
    
            if (dirname is not None) and (filename is not None):
                for item in the_results:
                    the_headers = the_headers.union(set(item.keys()))
                export_as_csv_file(list(the_headers), the_results, dirname, filename, verbose=is_verbose)
        
                if (is_uploading):
                    upload_to_google_drive(fname) # must debug this.
        else:
            print('WARNING: Problem with {} {}.'.format(url, r.status_code))

        return the_headers, the_results
    
    
    def special_column_filter(k, v, special_cols):
        new_key, new_value = _utils.ascii_only(k) if (isinstance(k, str)) else k, _utils.ascii_only(v) if (isinstance(v, str)) else v
        if (isinstance(k, str)) and (isinstance(v, str)) and (k.lower() == str(__location__).lower()):
            import re
            regex = r"(\([A-Za-z0-9]{3}-[A-Za-z0-9]{3}\))"
            matches = [m for m in re.finditer(regex, v, re.MULTILINE)]
            if (len(matches) > 0):
                new_key = new_value = None # signal the skipping of this row - skipped over Carriers.
        else:
            new_key = normalize_key(k)
            new_value = ''.join([c for c in v if (_utils.is_floating_or_numeric_digit(c))]) if (isinstance(v, str)) else v
            new_value = float(new_value) if (isinstance(new_key, float)) or (_utils.is_floating_or_numeric_digits(new_value)) else 0.0
            
        if (new_key is not None):
            new_special_cols = list(set(special_cols).union(set([new_key])))
            while (len(special_cols) > 0):
                special_cols.pop()
            for item in new_special_cols:
                special_cols.append(item)
        return tuple([new_key, new_value])


    def write_output(fOut, msg):
        try:
            if (isinstance(msg, str)):
                fOut.write(msg + '\n')
            else:
                fOut.write(msg.to_string() + '\n')
        except:
            try:
                fOut.put(msg if (isinstance(msg, str)) else msg.ro_string())
            except Exception as ex:
                sys.stderr.write(msg + '\n')


    def normalize_frame_keys(frame, specials):
        sCols = []
        try:
            keys = frame.keys()
            for col in specials:
                if (col in keys):
                    sCols.append(col)
        except Exception as ex:
            sys.stderr.write('{}\n'.format(ex))
        return sCols
    
    import pandas

    pandas.set_option('display.max_columns', None)
    pandas.set_option('display.width', 200)

    the_headers, buymin_results = fetch_data_from(commodities_buymin_url, dirname=dirname, filename='commodity_{}_buymin.csv'.format(__commodity_name__), is_verbose=False, is_debugging=False, filter_keys_for_callback=__special_cols__, callback=special_column_filter)
    
    df_buymin = pandas.DataFrame(buymin_results)

    colName = 'Buy_price_value'
    #print('(0) Min {}, Max {}, Mean {}'.format(df_buymin[colName].min(), df_buymin[colName].max(), df_buymin[colName].mean()))

    buymin_subDataFrame = harmonic_averages(df_buymin, colName, harmonic=3, min_qty=1000, qty_col_name='QTY_value')
    if (is_verbose):
        write_output(fOut, '(1) Min {}, Max {}, Mean {}'.format(buymin_subDataFrame[colName].min(), buymin_subDataFrame[colName].max(), buymin_subDataFrame[colName].mean()))
    buymin_price = buymin_subDataFrame[colName].min()
    if (is_verbose):
        write_output(fOut, buymin_subDataFrame[normalize_frame_keys(buymin_subDataFrame, __special_cols__)].dropna())

    fpath = os.sep.join([dirname, 'commodity_{}_buymin_locations.csv'.format(__commodity_name__)])
    with open(fpath, 'w') as ffOut:
        buymin_subDataFrame[normalize_frame_keys(buymin_subDataFrame, __special_cols__)].to_csv(sys.stdout if (is_verbose) else ffOut)
        ffOut.flush()

    the_headers, sellmax_results = fetch_data_from(commodities_sellmax_url, dirname=dirname, filename='commodity_{}_sellmax.csv'.format(__commodity_name__), is_verbose=False, is_debugging=False, filter_keys_for_callback=__special_cols__, callback=special_column_filter)
    
    df_sellmax = pandas.DataFrame(sellmax_results)

    colName = 'Sell_price_value'
    #print('(0) Min {}, Max {}, Mean {}'.format(df_sellmax[colName].min(), df_sellmax[colName].max(), df_sellmax[colName].mean()))

    sellmax_subDataFrame = harmonic_averages(df_sellmax, colName, harmonic=3, min_qty=1000, qty_col_name='QTY_value')
    if (is_verbose):
        write_output(fOut, '(1) Min {}, Max {}, Mean {}'.format(sellmax_subDataFrame[colName].min(), sellmax_subDataFrame[colName].max(), sellmax_subDataFrame[colName].mean()))
    sellmax_price = sellmax_subDataFrame[colName].min()
    
    try:
        fpath = os.sep.join([dirname, 'commodity_{}_sellmax_locations.csv'.format(__commodity_name__)])
        isnan_sellmax_price = math.isnan(sellmax_price)
        isnan_buymin_price = math.isnan(buymin_price)
        if (not isnan_sellmax_price) and (not isnan_buymin_price) and (int(sellmax_price / buymin_price) > 5):
            if (is_verbose):
                write_output(fOut, 'Locations with profit margin greater than 5:')
                write_output(fOut, sellmax_subDataFrame[normalize_frame_keys(sellmax_subDataFrame, __special_cols__)].dropna())
            with open(fpath, 'w') as ffOut:
                sellmax_subDataFrame[normalize_frame_keys(sellmax_subDataFrame, __special_cols__)].to_csv(sys.stdout if (is_verbose) else ffOut)
                ffOut.flush()
        elif (isnan_sellmax_price) or (isnan_buymin_price):
            with open(fpath, 'w') as ffOut:
                ffOut.write('WARNING: {}{}{}\n'.format('Max sell price is NaN.' if (isnan_sellmax_price) else '', ' or ' if (isnan_sellmax_price or isnan_buymin_price) else ' and ' if (isnan_sellmax_price and isnan_buymin_price) else '', 'Min buy price is NaN.' if (isnan_buymin_price) else ''))
                ffOut.flush()
    except Exception as ex:
        sys.stderr.write('WARNING: {}'.format(ex))

    #print(sellmax_subDataFrame)          
        
if (__name__ == '__main__'):
    scrape_commodity_data()
