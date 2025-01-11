from strep.index_scale import load_database, scale_and_rate
from strep.elex.app import Visualization
from main import DATABASES

databases = {}
for name, fname in DATABASES.items():
    print('LOADING', fname)
    database, meta = load_database(fname)
    databases[name] = scale_and_rate(database, meta)
    
app = Visualization(databases)
server = app.server
app.run_server(debug=False, host='0.0.0.0', port=10000)
