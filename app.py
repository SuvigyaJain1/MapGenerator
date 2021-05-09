import sys
import threading

from flask import Flask, render_template, send_from_directory, request, redirect, jsonify, url_for
from flask_cors import CORS
from main import hexagonal_lattice, displayMap, combine_polys, setBoundingOcean
from shapely.geometry import Polygon, MultiPolygon
from geovoronoi import voronoi_regions_from_coords
import os


app = Flask(__name__)
CORS(app)

sys.setrecursionlimit(1 << 20)    # adjust numbers
threading.stack_size(1 << 30)   # for your needs

params = {
    'ROWS': 5,
    'COLS': 5,
    'NOISE': 0.03,
    'OCEAN': 1,
    'HEXAGON_FILE': "testing.png",
    'COLORED_W_OCEAN_FILE': "test.png",
    'WKT_FILE': "test.txt",
    'DISTRIBUTION': [0.40, 0.3, 0.05, 0, 0.1, 0.15],
}


def image_gen_main():
    coords = hexagonal_lattice(params['ROWS'], params['COLS'], params['NOISE'])[:, :2]
    x_min, x_max, y_min, y_max = coords[:, 0].min(), coords[:, 0].max(), coords[:, 1].min(), coords[:, 1].max()
    bounding_box = Polygon([(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min)])
    region_polys, _ = voronoi_regions_from_coords(coords, bounding_box)
    dirname = "/home/suvigya/PycharmProjects/MapGeneratorApp/images/"

    ocean = 0.07
    if int(params['OCEAN']) == 0:
        ocean = 0

    displayMap(list(region_polys.values()), filename=dirname+params['HEXAGON_FILE'], bounds=bounding_box.bounds)

    multi = []
    for poly in region_polys:
        multi.append(region_polys[poly])

    multi = MultiPolygon(multi)
    cmap = combine_polys(multi, params['DISTRIBUTION'])

    if ocean != 0:
        setBoundingOcean(multi, bounding_box.boundary,
                         bounds=(x_max, x_min), cmap=cmap,
                         buffer=ocean, noise=float(params['NOISE']))
    else:
        setBoundingOcean(multi, bounding_box.boundary, bounds=(x_max, x_min), cmap=cmap, buffer=0, noise=0.00)

    displayMap(multi, fillcolors=cmap, filename=dirname+params['COLORED_W_OCEAN_FILE'], bounds=bounding_box.bounds)

    with open(dirname+params['WKT_FILE'], "w") as fp:
        fp.write(multi.wkt)
    del multi, cmap, region_polys, coords,


@app.route('/uploads/<path:filename>')
def get_image(filename):
    return send_from_directory("/home/suvigya/PycharmProjects/MapGeneratorApp/images", filename, as_attachment=True)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', img=url_for('get_image', filename=params['COLORED_W_OCEAN_FILE']))


@app.route('/generate', methods=['POST'])
def generate_images():
    main_thread = threading.Thread(target=image_gen_main)
    main_thread.start()
    main_thread.join()
    render_template('index.html', img=url_for('get_image', filename=params['COLORED_W_OCEAN_FILE']))
    redirect('/')
    return jsonify(success="image successfully generated",
                   image=params['COLORED_W_OCEAN_FILE'])


@app.route('/setParams', methods=['POST'])
def set_params():
    # return request.form
    for key in list(params.keys()):
        val = request.form.get(key)
        if val is not None:
            params[key] = request.form[key]

    # params['COLORED_W_OCEAN_FILE'] = os.path.join("images", params['COLORED_W_OCEAN_FILE'])
    # params['WKT_FILE'] = os.path.join("images", params['WKT_FILE'])
    # params['HEXAGON_FILE'] = os.path.join("images", params['HEXAGON_FILE'])

    return jsonify(success="Updated params. Ready to generate image", params=params)


if __name__ == 'main':
    app.run(debug=True)
