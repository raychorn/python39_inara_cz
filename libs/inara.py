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
    

def scrape_commodity_data():
    import requests
    import simplejson

    from vyperlogix import enum
    
    from bs4 import BeautifulSoup
    
    from io import StringIO
    
    commodities = {}
    
    __tritium__ = 'Tritium'

    class RefName(enum.Enum.Enum):
        buymin=0
        sellmax=1
    class Items(enum.Enum.Enum):
        tritium=10269
    class Systems(enum.Enum.Enum):
        tritium=10269
    tritium_url = "https://inara.cz/ajaxaction.php?act=goodsdata&refname=buymin&refid=10269&refid2=367"     # refid is the commodity, refid2 is the star system.
    tritium_url2 = "https://inara.cz/ajaxaction.php?act=goodsdata&refname=buymin&refid=10269&refid2=18698"
    tritium_url3 = "https://inara.cz/ajaxaction.php?act=goodsdata&refname=sellmax&refid=10269&refid2=18698"
    
    commodities_url1 = "https://inara.cz/galaxy-commodity/10269/"
    commodities_url2 = "https://inara.cz/ajaxaction.php?act=goodsdata&refname=buymin&refid=10269&refid2=0"
    commodities_url3 = "https://inara.cz/ajaxaction.php?act=goodsdata&refname=sellmax&refid=10269&refid2=0"

    headers = []
    results = []
    
    r = requests.get(commodities_url2)
    if (r.ok):
        soup = BeautifulSoup(r.content, 'html.parser')
        tables = soup.findAll(name='table', attrs={'class':"tablesorter"})
        for table in tables:
            headers = [header.text for header in table.find_all('th')]
            results = [{headers[i]: cell for i, cell in enumerate(row.find_all('td'))}
                       for row in table.find_all('tr')]
            the_results = []
            for result in results:
                if (len(result.keys()) > 0):
                    row = {}
                    for k,v in result.items():
                        row[k] = v.getText()
                    the_results.append(row)
            break
        # dump the dict into a SQLite Db Table.
        fOut = StringIO()
        fOut.write('class Commodities(enum.Enum.Enum):\n')
        for k,v in commodities.items():
            fOut.write('{}{}={}\n'.format(' '*4,k,v))
        fOut.flush()
        lines = fOut.getvalue().split('\n')
        for l in lines:
            print(l)
        fOut.close()
        for div in divs:
            for child in div.children:
                pass
    else:
        print('WARNING: Problem with {} {}.'.format(commodities_url1, r.status_code))
    
if (__name__ == '__main__'):
    scrape_commodity_data()
    