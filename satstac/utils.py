import base64
import calendar
import datetime
import hashlib
import hmac
import logging
import os
import requests
import sys
import time

from collections.abc import Mapping

logger = logging.getLogger(__name__)


# from https://gist.github.com/angstwad/bf22d1822c38a92ec0a9#gistcomment-2622319
def dict_merge(dct, merge_dct, add_keys=True):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.

    This version will return a copy of the dictionary and leave the original
    arguments untouched.

    The optional argument ``add_keys``, determines whether keys which are
    present in ``merge_dict`` but not ``dct`` should be included in the
    new dict.

    Args:
        dct (dict) onto which the merge is executed
        merge_dct (dict): dct merged into dct
        add_keys (bool): whether to add new keys

    Returns:
        dict: updated dict
    """
    dct = dct.copy()
    if not add_keys:
        merge_dct = {
            k: merge_dct[k]
            for k in set(dct).intersection(set(merge_dct))
        }

    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], Mapping)):
            dct[k] = dict_merge(dct[k], merge_dct[k], add_keys=add_keys)
        else:
            dct[k] = merge_dct[k]

    return dct


def download_file(url, filename=None, requester_pays=False, headers={}):
    """ Download a file as filename """
    filename = os.path.basename(url) if filename is None else filename
    logger.info('Downloading %s as %s' % (url, filename))
    _path = os.path.dirname(filename)
    if not os.path.exists(_path):
        mkdirp(_path)
    # check if on s3, if so try to sign it
    if 's3.amazonaws.com' in url:
        signed_url, signed_headers = get_s3_signed_url(url, requester_pays=requester_pays)
        resp = requests.get(signed_url, headers=signed_headers, stream=True)
        if resp.status_code != 200:
            resp = requests.get(url, headers=headers, stream=True)
    elif 'eosdis.nasa.gov' in url:
        url = url.replace('/archive/', '/api/v2/content/archives/')
        resp = requests.get(url, headers=headers, stream=True)
    else:
        resp = requests.get(url, headers=headers, stream=True)
    if resp.status_code != 200:
        raise Exception("Unable to download file %s: %s" % (url, resp.text))
    with open(filename, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return filename

def mkdirp(path):
    """ Recursively make directory """
    if not os.path.isdir(path) and path != '':
        os.makedirs(path)
    return path


# from https://www.oreilly.com/library/view/python-cookbook/0596001673/ch04s16.html
def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


def get_s3_signed_url(url, rtype='GET', public=False, requester_pays=False, content_type=None):
    access_key = os.environ.get('AWS_BUCKET_ACCESS_KEY_ID', os.environ.get('AWS_ACCESS_KEY_ID'))
    secret_key = os.environ.get('AWS_BUCKET_SECRET_ACCESS_KEY', os.environ.get('AWS_SECRET_ACCESS_KEY'))
    region = os.environ.get('AWS_BUCKET_REGION', os.environ.get('AWS_REGION', 'eu-central-1'))
    if access_key is None or secret_key is None:
        # if credentials not provided, just try to download without signed URL
        logger.debug('Not using signed URL for %s' % url)
        return url, None

    parts = url.replace('https://', '').split('/')
    bucket = parts[0].replace('.s3.amazonaws.com', '')
    key = '/'.join(parts[1:])

    service = 's3'
    host = '%s.s3.amazonaws.com' % (bucket)
    request_parameters = ''

    # Key derivation functions. See:
    # http://docs.aws.amazon.com/general/latest/gr/signature-v4-examples.html#signature-v4-examples-python
    def sign(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    def getSignatureKey(key, dateStamp, regionName, serviceName):
        kDate = sign(('AWS4' + key).encode('utf-8'), dateStamp)
        kRegion = sign(kDate, regionName)
        kService = sign(kRegion, serviceName)
        kSigning = sign(kService, 'aws4_request')
        return kSigning

    # Create a date for headers and the credential string
    t = datetime.datetime.utcnow()
    amzdate = t.strftime('%Y%m%dT%H%M%SZ')
    datestamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope

    # create signed request and headers
    canonical_uri = '/' + key
    canonical_querystring = request_parameters

    payload_hash = 'UNSIGNED-PAYLOAD'
    headers = {
        'host': host,
        'x-amz-content-sha256': payload_hash,
        'x-amz-date': amzdate
    }
    if requester_pays:
        headers['x-amz-request-payer'] = 'requester'
    if public:
        headers['x-amz-acl'] = 'public-read'
    if os.environ.get('AWS_SESSION_TOKEN') and 'AWS_BUCKET_ACCESS_KEY_ID' not in os.environ:
        headers['x-amz-security-token'] = os.environ.get('AWS_SESSION_TOKEN')
    canonical_headers = '\n'.join('%s:%s' % (key, headers[key]) for key in sorted(headers)) + '\n'
    signed_headers = ';'.join(sorted(headers.keys()))

    canonical_request = '%s\n%s\n%s\n%s\n%s\n%s' % (
        rtype, canonical_uri, canonical_querystring, canonical_headers, signed_headers, payload_hash
    )
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = datestamp + '/' + region + '/' + service + '/' + 'aws4_request'
    string_to_sign = algorithm + '\n' +  amzdate + '\n' +  credential_scope + '\n' +  hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
    signing_key = getSignatureKey(secret_key, datestamp, region, service)
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    authorization_header = algorithm + ' ' + 'Credential=' + access_key + '/' + credential_scope + ', ' \
        + 'SignedHeaders=' + signed_headers + ', ' + 'Signature=' + signature

    request_url = 'https://%s%s' % (host, canonical_uri)
    headers['Authorization'] = authorization_header
    if content_type is not None:
        headers['content-type'] = content_type
    return request_url, headers


def terminal_calendar(events, cols=3):
    """ Get calendar covering all dates, with provided dates colored and labeled """
    if len(events.keys()) == 0:
        return ''
    # events is {'date': 'label'}
    _dates = sorted(events.keys())
    _labels = set(events.values())
    labels = dict(zip(_labels, [str(41 + i) for i in range(0, len(_labels))]))

    start_year = _dates[0].year
    end_year = _dates[-1].year

    # start and end rows
    row1 = int((_dates[0].month - 1) / cols)
    row2 = int((_dates[-1].month - 1) / cols) + 1

    # generate base calendar array
    Calendar = calendar.Calendar()
    cal = []
    for yr in range(start_year, end_year+1):
        ycal = Calendar.yeardatescalendar(yr, width=cols)
        if yr == start_year and yr == end_year:
            ycal = ycal[row1:row2]
        elif yr == start_year:
            ycal = ycal[row1:]
        elif yr == end_year:
            ycal = ycal[:row2]
        cal.append(ycal)

    # month and day headers
    months = calendar.month_name
    days = 'Mo Tu We Th Fr Sa Su'
    hformat = '{:^20}  {:^20}  {:^20}\n'
    rformat = ' '.join(['{:>2}'] * 7) + '  '

    # create output
    col0 = '\033['
    col_end = '\033[0m'
    out = ''
    for iy, yrcal in enumerate(cal):
        out += '{:^64}\n\n'.format(_dates[0].year + iy)
        for mrow in yrcal:
            mnum = mrow[0][2][3].month
            names = [months[mnum], months[mnum+1], months[mnum+2]]
            out += hformat.format(names[0], names[1], names[2])
            out += hformat.format(days, days, days)
            for r in range(0, len(mrow[0])):
                for c in range(0, cols):
                    if len(mrow[c]) == 4:
                        mrow[c].append([''] * 7)
                    if len(mrow[c]) == 5:
                        mrow[c].append([''] * 7)
                    wk = []
                    for d in mrow[c][r]:
                        if d == '' or d.month != (mnum + c):
                            wk.append('')
                        else:
                            string = str(d.day).rjust(2, ' ')
                            if d in _dates:
                                string = '%s%sm%s%s' % (col0, labels[events[d]], string, col_end)
                            wk.append(string)
                    out += rformat.format(*wk)
                out += '\n'
            out += '\n'
    # print labels
    for lbl, col in labels.items():
        vals = list(_labels)
        out += '%s%sm%s (%s)%s\n' % (col0, col, lbl, vals.count(lbl), col_end)
    out += '%s total dates' % len(_dates)
    return out
