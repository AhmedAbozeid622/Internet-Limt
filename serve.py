from flask import Flask , Response
app = Flask(__name__)
from server.ETIS_API import ETIS_API
import json
App = ETIS_API()

@app.route('/')
def get():
    data = App.getGenericConsumptions()
    return Response(json.dumps(data) , status=200 , mimetype='application/json')
    
    # return str()
@app.route('/getPayments')
def get_payments():
    data = App.getOpenAmount()
    return Response(json.dumps(data) , status=200 , mimetype='application/json')

app.run(debug=False)


