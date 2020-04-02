from flask import Flask, jsonify, render_template, request, redirect, url_for, make_response
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
from models import ModelController
from processData import ProcessData
import matplotlib
matplotlib.use('Agg')
app = Flask(__name__)
COUNT = 0
last_img = ''

ctrl = ModelController()


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


    return position_data



@app.route("/plot_positions", methods=["GET"])
def plot_positions():
    return render_template('/layouts/get_data.html')

#ESTA FUNCION DEVOLVERÁ UN JSON CON LAS POSICIONES DE LOS MOVILES.
#ESTA FUNCION SERÁ LLAMADA POR EL JAVASCRIPT ENCASTADO EN EL HTML DE get_data.html
def get_devices_positions():
    pd = ProcessData()
    result = pd.estimatePosition()
    return result

'''
#ESTA FUNCION DEVOLVERA UN JSON CON LAS POSICIONES DE LOS ANCHORS
#ESTA FUNCION SERÁ LLAMADA POR EL JAVASCRIPT ENCASTADO EN EL HTML DE get_data.html

def get_anchors_position():
    with open("position.yml", 'r') as posfile:
        anchor_pos = yaml.load(posfile)
        result = dict()
        name_anchor_1 = anchor_pos["anchorsInfo"]["anchor1"]["name"]
        result[name_anchor_1] = dict()
        result[name_anchor_1]['X'] = anchor_pos["anchorsInfo"]["anchor1"]['X']
        result[name_anchor_1]['Y'] = anchor_pos["anchorsInfo"]["anchor1"]['Y']

        name_anchor_2 = anchor_pos["anchorsInfo"]["anchor2"]["name"]
        result[name_anchor_2] = dict()
        result[name_anchor_2]['X'] = anchor_pos["anchorsInfo"]["anchor2"]['X']
        result[name_anchor_2]['Y'] = anchor_pos["anchorsInfo"]["anchor2"]['Y']

        name_anchor_3 = anchor_pos["anchorsInfo"]["anchor3"]["name"]
        result[name_anchor_3] = dict()
        result[name_anchor_3]['X'] = anchor_pos["anchorsInfo"]["anchor3"]['X']
        result[name_anchor_3]['Y'] = anchor_pos["anchorsInfo"]["anchor3"]['Y']

        return result

'''

@app.route("/positions_img", methods=["GET"])
def positions_img():
    global last_img
    # creamos la imagen. Será un plot de matplotlib con los anchors y los devices. retorna un png

    dev_pos = ctrl.getDevicesPositions()
    anchors_pos = ctrl.getAnchorsPositions()
    print(dev_pos)
    print()
    print(anchors_pos)

    #imprimimos los anchors (launchpads) primeramente.

    x = []
    y = []
    anc_names = []
    for a in anchors_pos:
        x.append(float(anchors_pos[a]['X']))
        y.append(float(anchors_pos[a]['Y']))
        anc_names.append(a)

    fig, ax = plt.subplots()
    plt.xlim((ctrl.getRoomXMin(), ctrl.getRoomXMax()))
    plt.ylim((ctrl.getRoomYMin(), ctrl.getRoomYMax()))
    ax.scatter(x,y,c='r')

    for i, txt in enumerate(anc_names):
        ax.annotate(txt, (x[i],y[i]))

    # imprimimos los devices (móviles) a continuación.

    x = []
    y = []
    dev_names = []
    try:
        for d in dev_pos:
            x.append(float(dev_pos[d]['X']))
            y.append(float(dev_pos[d]['Y']))
            dev_names.append(d)


        ax.scatter(x, y, c='b')

        for i, txt in enumerate(dev_names):
            ax.annotate(txt, (x[i], y[i]))

        ax.set(xlabel='distance (m)', ylabel='distance (m)',
               title='Positions')
        ax.grid()

    except KeyError:
        return last_img


    #NO TOCAR A PARTIR DE AQUI!
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
    next = request.args.get('next', None)
    return redirect(url_for('plot_positions'))


if __name__ == '__main__':

    app.run(host="0.0.0.0", port=4000, debug=True)
