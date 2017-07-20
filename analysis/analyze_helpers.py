import sys
import json


def load_test_metadata(metadata_path):
    with open(metadata_path) as metadata:
        return json.load(metadata)


def verify_schemes_with_meta(schemes, meta):
    all_schemes = meta['cc_schemes']

    if schemes is None:
        return all_schemes

    cc_schemes = schemes.split()

    for cc in cc_schemes:
        if cc not in all_schemes:
            sys.exit('%s is not a scheme included in '
                     'pantheon_metadata.json' % cc)

    return cc_schemes
