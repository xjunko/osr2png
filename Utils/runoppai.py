import json
import os
import subprocess

def runOppai(command):
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        output = json.loads(process.stdout.decode('utf-8', errors='ignore'))
        if output['code'] != 200:
            raise RuntimeError('oppai fucking die')
        if 'pp' not in output or 'stars' not in output:
            raise RuntimeError('sad oppai no give data')

        pp = output['pp']
        stars = output['stars']
    except (json.JSONDecodeError, IndexError) as e:
        raise RuntimeError('oppai go gay mode sorry')

    return pp, stars


