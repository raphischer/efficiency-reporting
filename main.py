import argparse
import os
import time

from strep.index_scale import load_database, scale_and_rate
from strep.util import load_meta
from strep.elex.app import Visualization

DATABASES = {
    # 'Papers With Code': 'databases/paperswithcode/database.pkl',
    # 'MetaQuRe': 'databases/metaqure/database.pkl',
    'ImageNetEff': 'databases/imagenet_classification/database.pkl',
    'RobustBench': 'databases/robustbench/database.pkl',
    'Forecasting': 'databases/xpcr/database.pkl'
}

def preprocess_database(fname):
    if not os.path.isfile(fname):
        raise RuntimeError('Could not find', fname)
    # load database
    database = load_database(fname)
    if 'paperswithcode' in fname:
        database['dataset'] = database['dataset'].map(lambda val: 'KITTI' if val == 'kitti-depth-completion' else val)
    # load meta infotmation
    meta = load_meta(os.path.dirname(fname))
    # rate database
    rated_database, boundaries, real_boundaries, defaults = scale_and_rate(database, meta)
    return rated_database, meta, defaults, boundaries, real_boundaries, None

if __name__ == '__main__':    

    parser = argparse.ArgumentParser()

    parser.add_argument("--mode", default='interactive', choices=['interactive', 'paper_results'])
    parser.add_argument("--database", default=None)
    # interactive exploration params
    parser.add_argument("--host", default='localhost', type=str, help="default host") # '0.0.0.0'
    parser.add_argument("--port", default=8888, type=int, help="default port")
    parser.add_argument("--debug", default=False, type=bool, help="debugging")

    args = parser.parse_args()

    if args.database is not None:
        DATABASES = {'CUSTOM': args.database}

    databases = {}
    for name, fname in DATABASES.items():
        print('LOADING', fname)
        databases[name] = preprocess_database(fname)
        # override defaults for robustbench
        if 'robustbench' in fname:
            for ds_task in databases[name][2].keys():
                databases[name][3][ds_task] = 'clean_acc' # x axis
                databases[name][4][ds_task] = 'autoattack_acc' # y axis

    app = Visualization(databases, use_pages=True, pages_folder='')
    server = app.server
        
    app.run_server(debug=args.debug, host=args.host, port=args.port)
