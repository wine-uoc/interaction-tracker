from flask import Flask, jsonify, render_template, request, redirect, url_for
import json
import psycopg2
import yaml

from accessDB import DB
from processData import ProcessData

app = Flask(__name__)

def saveConfigToYML():
    with open('position.yml', 'w') as ymlfile:
        position_data = dict()
        position_data['anchorsInfo'] = dict()
        position_data['anchorsInfo']['anchor1'] = dict()
        position_data['anchorsInfo']['anchor2'] = dict()
        position_data['anchorsInfo']['anchor3'] = dict()

        position_data['anchorsInfo']['anchor1']['name'] = str(request.form['id-a1'])
        position_data['anchorsInfo']['anchor1']['X'] = request.form['a1-x']
        position_data['anchorsInfo']['anchor1']['Y'] = request.form['a1-y']

        position_data['anchorsInfo']['anchor2']['name'] = str(request.form['id-a2'])
        position_data['anchorsInfo']['anchor2']['X'] = request.form['a2-x']
        position_data['anchorsInfo']['anchor2']['Y'] = request.form['a2-y']

        position_data['anchorsInfo']['anchor3']['name'] = str(request.form['id-a3'])
        position_data['anchorsInfo']['anchor3']['X'] = request.form['a3-x']
        position_data['anchorsInfo']['anchor3']['Y'] = request.form['a3-y']

        yaml.dump(position_data, ymlfile)

# ESTE METODO HA DE DEVOLVER UN JSON (EN VEZ DE HTML) CADA VEZ QUE NODE-RED (FRONT-END) PIDA DATOS DE LA POSICION DE TODOS LOS DISPOSITIVOS!

@app.route("/get_data", methods=["GET", "POST"])
def get_data():
    pd = ProcessData()
    result = pd.estimate_position()
    launchpadIds = pd.getLaunchpadIds()
    jsonify(result)
    return render_template("update-position.html", d1=result[launchpadIds[0]], d2=result[launchpadIds[1]], d3=result[launchpadIds[2]])

@app.route("/", methods=["GET", "POST"])
def show_signup_form():
    if request.method == "POST":
        saveConfigToYML()
        next = request.args.get('next', None)

        return redirect(url_for('get_data'))

    return render_template("data_form.html")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4000, debug=True)


