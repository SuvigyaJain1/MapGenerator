import sys
import threading

from flask import Flask, render_template, send_from_directory, request, redirect, jsonify, url_for, session
# from flask.ext.session import Session
from flask_cors import CORS
from main import hexagonal_lattice, displayMap, combine_polys, setBoundingOcean
from shapely.geometry import Polygon, MultiPolygon
from geovoronoi import voronoi_regions_from_coords
import os
from random import randint

app = Flask(__name__)
app.secret_key = str(randint(0,10000000))

# SESSION_TYPE = 'redis'
app.config.from_object(__name__)
# Session(app)
CORS(app)

# sys.setrecursionlimit(1 << 20)    # adjust numbers
# threading.stack_size(1 << 30)   # for your needs

params = {
    'ROWS': 5,
    'COLS': 5,
    'NOISE': 0.03,
    'OCEAN': 0,
    'HEXAGON_FILE': "testing.png",
    'COLORED_W_OCEAN_FILE': "test_hex.png",
    'WKT_FILE': "test.txt",
    'DISTRIBUTION': [0.40, 0.3, 0.05, 0, 0.1, 0.15],
}


def image_gen_main():
    coords = hexagonal_lattice(session['ROWS'], session['COLS'], session['NOISE'])[:, :2]
    x_min, x_max, y_min, y_max = coords[:, 0].min(), coords[:, 0].max(), coords[:, 1].min(), coords[:, 1].max()
    bounding_box = Polygon([(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min)])
    region_polys, _ = voronoi_regions_from_coords(coords, bounding_box)
    dirname = "/home/suvigya/PycharmProjects/MapGeneratorApp/images/"

    ocean = 0.07
    if int(session['OCEAN']) == 0:
        ocean = 0

    displayMap(list(region_polys.values()), filename=dirname+session['HEXAGON_FILE'], bounds=bounding_box.bounds)

    multi = []
    for poly in region_polys:
        multi.append(region_polys[poly])

    multi = MultiPolygon(multi)
    cmap = combine_polys(multi, session['DISTRIBUTION'])

    if ocean != 0:
        setBoundingOcean(multi, bounding_box.boundary,
                         bounds=(x_max, x_min), cmap=cmap,
                         buffer=ocean, noise=float(session['NOISE']))
    else:
        setBoundingOcean(multi, bounding_box.boundary, bounds=(x_max, x_min), cmap=cmap, buffer=0, noise=0.00)

    displayMap(multi, fillcolors=cmap, filename=dirname+session['COLORED_W_OCEAN_FILE'], bounds=bounding_box.bounds)

    with open(dirname+session['WKT_FILE'], "w") as fp:
        fp.write(multi.wkt)
    del multi, cmap, region_polys, coords,


@app.route('/uploads/<path:filename>')
def get_image(filename):
    return send_from_directory("/home/suvigya/PycharmProjects/MapGeneratorApp/images", filename, as_attachment=True)


@app.route('/', methods=['GET'])
def index():
    for key in list(params.keys()):
        if key not in session:
            session[key] = params[key]
    return render_template('index.html', img=url_for('get_image', filename=session['COLORED_W_OCEAN_FILE']))


@app.route('/generate', methods=['POST'])
def generate_images():
    image_gen_main()
    return jsonify(success="image successfully generated",
                   image=session['COLORED_W_OCEAN_FILE'])


@app.route('/setParams', methods=['POST'])
def set_session():
    # return request.form
    for key in list(params.keys()):
        val = request.form.get(key)
        if val is not None:
            session[key] = val
    session['DISTRIBUTION'] = request.form.getlist('DISTRIBUTION[]')
    return jsonify(success="Updated session. Ready to generate image")


if __name__ == 'main':
    app.run(debug=True)
