#!/usr/local/bin/python3

# https://raw.githubusercontent.com/molamk/gpt2-react-flask/master/server/main.py


from flask import Flask, abort, jsonify, request
from flask_cors import CORS, cross_origin

import gpt_2_simple as gpt2
import tensorflow as tf
import uvicorn
import os
import gc

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

sess = gpt2.start_tf_sess(threads=1)
gpt2.load_gpt2(sess)

generate_count = 0

@app.route("/", methods=['GET', 'POST', 'HEAD'])
@cross_origin()
async def homepage(request):
    global generate_count
    global sess

    if request.method == 'GET':
        params = request.query_params
    elif request.method == 'POST':
        params = await request.json()
    elif request.method == 'HEAD':
        return UJSONResponse({'text': ''},
                             headers=response_header)

    text = gpt2.generate(sess,
                         model_name="quora",
                         length=int(params.get('length', 1023)),
                         temperature=float(params.get('temperature', 1.0)),
                         top_k=int(params.get('top_k', 0)),
                         top_p=float(params.get('top_p', 0)),
                         prefix=params.get('prefix', '')[:500],
                         truncate=params.get('truncate', None),
                         nsamples=5,
                         batch_size=5,
                         include_prefix=str(params.get(
                             'include_prefix', True)).lower() == 'true',
                         return_as_list=True
                         )[0]

    generate_count += 1
    if generate_count == 8:
        # Reload model to prevent Graph/Session from going OOM
        tf.reset_default_graph()
        sess.close()
        sess = gpt2.start_tf_sess(threads=1)
        gpt2.load_gpt2(sess)
        generate_count = 0

    gc.collect()
    return UJSONResponse({'text': text},
                         headers=response_header)

if __name__ == '__main__':
    app.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
