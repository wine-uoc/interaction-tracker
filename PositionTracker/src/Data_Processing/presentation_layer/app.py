import threading

from flask import Flask, jsonify, render_template, request, redirect, url_for, make_response
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
import sched, time
import sys

from src.Data_Processing.domain_layer.models import ModelController

sys.path.insert(1,'../domain_layer')
from models import *
import matplotlib
import yaml
import numpy as np
import signal, os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

matplotlib.use('Agg')
app = Flask(__name__)
COUNT = 0
last_img = ''

ctrl = ModelController()
show_circles = False
show_rssi = False

file = open('../config.yml', 'r')
cfg = yaml.load(file)

TEST_MODEL = cfg['pythonApp']['testing']
num_samples = 0
MAX_SAMPLES = 100


# funcion que calcula la posicion de los dispositivos (target)
def computeDevicesPositions():
    try:
        ctrl.computeDevicesPositions()
    except ValueError:
        print(
            "ValueError!, seguramente es porque al borrarse datos antiguos de la BD, los distintos dispositivos (moviles o launchpads) que habian no son los mismos que los que hay despues de borrarla.")


# this function is called periodically in order to delete the oldest DB data
def triggerDeleteOldestDBdata():
    ctrl.triggerDeleteFromDBoldestData()


# Inicializa el scheduler para que compute el valor de la posicion cada X ms (definido en config.yml -> cfg['pythonApp']['TComputePositions'] )
executors = {
    'default': ThreadPoolExecutor(16),
    'processpool': ProcessPoolExecutor(4)
}
schedu = BackgroundScheduler(executors=executors)
schedu.add_job(computeDevicesPositions, 'interval',
               seconds=cfg['pythonApp']['TComputePositions'])  # Thread que computa la posicion del dispositivo
schedu.add_job(triggerDeleteOldestDBdata, 'interval',
               seconds=cfg['pythonApp']['TDeleteDB'])  # Thread que elimina datos antiguos de la BBDD.


# retrieve form data from 0.0.0.0:5000/
def extract_form_data():
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

    position_data['roomInfo'] = dict()
    position_data['roomInfo']['X_min'] = request.form['room-x-min']
    position_data['roomInfo']['X_max'] = request.form['room-x-max']
    position_data['roomInfo']['Y_min'] = request.form['room-y-min']
    position_data['roomInfo']['Y_max'] = request.form['room-y-max']
    position_data['roomInfo']['orientation'] = float(request.form['degree-north']) * (3.141592 / 180)  # degrees to rad.

    return position_data


@app.route("/plot_positions", methods=["GET"])
def plot_positions():
    return render_template('/layouts/get_data.html', circles=show_circles, rssi=show_rssi)


@app.route("/positions_img", methods=["GET", "POST"])
def positions_img():
    global last_img, num_samples
    global show_circles
    global show_rssi

    if request.method == 'POST':
        plotopts = request.form.getlist('plotopt')
        print(plotopts)
        if "Circles" in plotopts:
            show_circles = True
        else:
            show_circles = False

        if "RSSI" in plotopts:
            show_rssi = True
        else:
            show_rssi = False

        return redirect(url_for('plot_positions'))

    # creamos la imagen. Será un plot de matplotlib con los anchors y los devices. retorna un png
    if request.method == 'GET':
        dev_pos = ctrl.getDevicesPositions()
        anchors_pos = ctrl.getLaunchpadPositions()
        # print("estimated position RSSI+ACC+ORI: ")
        # print(dev_pos)
        # print()

        # imprimimos los anchors (launchpads) primeramente.

        x_anc = []
        y_anc = []
        anc_names = []
        for a in anchors_pos:
            x_anc.append(float(anchors_pos[a]['X']))
            y_anc.append(float(anchors_pos[a]['Y']))
            anc_names.append(a)

        fig, ax = plt.subplots()
        plt.xlim((ctrl.getRoomXMin(), ctrl.getRoomXMax()))
        plt.ylim((ctrl.getRoomYMin(), ctrl.getRoomYMax()))
        color_array = ["green", "yellow", "purple"]
        ax.scatter(x_anc, y_anc, c=color_array)

        for i, txt in enumerate(anc_names):
            ax.text(x_anc[i], y_anc[i], txt, fontsize=14)
        # ax.annotate(txt, (x_anc[i],y_anc[i]))

        # imprimimos los devices (móviles) a continuación.

        x_dev = []
        y_dev = []
        dev_names = []
        try:
            dot_colors = []
            for d in dev_pos:
                x_dev.append(float(dev_pos[d]['X']))
                y_dev.append(float(dev_pos[d]['Y']))
                dev_names.append(d)
                dot_colors.append('b')

            ax.scatter(x_dev, y_dev, c=dot_colors)

            if TEST_MODEL:
                x = cfg['pythonApp']['x_pos'] / 100
                y = cfg['pythonApp']['y_pos'] / 100
                devname = cfg['pythonApp']['deviceName']

                ax.scatter(x, y, c='orange')
                ax.text(x, y, devname, fontsize=14)
                x_est = dev_pos[devname]['X']
                y_est = dev_pos[devname]['Y']
                err = np.sqrt(pow(x_est - x, 2.0) + pow(y_est - y, 2.0))
                print(f"error: {err}")

                # insert the estimation error data into a file.
                if num_samples < MAX_SAMPLES:
                    with open("errorTest_x_" + str(cfg['pythonApp']['x_pos']) + "_y_" + str(cfg['pythonApp']['y_pos']) + ".txt", "a+") as file:
                        file.write(str(err) + '\n')
                        num_samples += 1
                else:
                    print("MAX_SAMPLES REACHED!!!")

            for i, txt in enumerate(dev_names):
                ax.text(x_dev[i], y_dev[i], txt, fontsize=14)

            ax.set(xlabel='distance (m)', ylabel='distance (m)', title='Positions')
            ax.grid()

            # imprimimos los circulos de alcance de los anchors. Miramos si el usuario lo pide.
            # DE MOMENTO SUPONEMOS QUE SOLO HAY 1 DEVICE. PARA MAS DE UNO, HABRÁ QUE DAR A ESCOGER AL USUARIO
            # DE CUAL QUIERE VER LOS CIRCULOS Y LA RSSI.

            if show_circles:  # usuario pide que se muestren los circulos
                res = list(zip(x_anc, y_anc, anc_names))
                i = 0
                for x, y, name in res:
                    ax.add_artist(
                        plt.Circle((x, y), ctrl.getRadiusFromAnchorToDevice(name, "TARGETDEV-1yfqac"),
                                   color=color_array[i],
                                   alpha=0.25))
                    i += 1

            if show_rssi:

                for devname in dev_names:
                    for i, anc_name in enumerate(anc_names):
                        rssi = ctrl.getRssiFromLaunchpadOfDevice(anc_name, devname)
                        ax.text(x_anc[i], y_anc[i] - 0.15, 'RSSI: ' + str(rssi), weight="bold")


        except KeyError:
            print(last_img)
            return last_img

        # NO TOCAR A PARTIR DE AQUI!
        canvas = FigureCanvas(fig)
        plt.close(fig)
        output = io.BytesIO()
        canvas.print_png(output)
        response = make_response(output.getvalue())
        response.mimetype = 'image/png'
        last_img = response
        return response


@app.route("/", methods=["GET"])
def get_data_form():
    return render_template("/layouts/data_form.html")


@app.route("/", methods=["POST"])
def post_data_form():
    ret = extract_form_data()
    ctrl.initialize(ret)
    schedu.start()
    ctrl.computeDevicesPositions()
    return redirect(url_for('plot_positions'))


###
### END FLASK APPLICATION
###


def main():
    app.run(host=cfg['pythonApp']['appHost'], port=int(cfg['pythonApp']['appPort']), debug=True)


if __name__ == '__main__':
    main()