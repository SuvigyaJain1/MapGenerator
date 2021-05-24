# !pip install geovoronoi descartes shapely

import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import MultiPolygon
from graph import Graph
import descartes
from random import choice
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg


def displayPolygon(polygon, h_ax=None, filename=None, fillcolor=None, linecolor=None, linewidth=0.0, alpha=1):
    """
    Takes a polygon or multipolygon and displays it using matplotlib. Also optionally accepts
    axes handler. If no axes handler passed then new figure is created
    If filename is provided then image is written to file instead of display
    """

    if h_ax is None:
        x_min, y_min, x_max, y_max = polygon.bounds
        fig = plt.figure(1, dpi=100)
        ax = fig.add_subplot(1, 1, 1)
        ax.set_ylim(y_min - 1, y_max + 1)
        ax.set_xlim(x_min - 1, x_max + 1)
    else:
        ax = h_ax

    if linecolor is None:
        linecolor = fillcolor

    patch = descartes.PolygonPatch(
        polygon, fc=fillcolor, ec=linecolor, linewidth=linewidth, alpha=alpha)
    ax.add_patch(patch)

    if h_ax is None:
        if filename is None:
            plt.show()
        else:
            plt.savefig(filename)


def displayMap(polygons, bounds, fillcolors=None, filename=None, linecolors=None):
    """
    Stitches together the map from the list of polygons or multipolygons.
    Cmap should be ordered list of hex color-codes of same size as polygons.
    """

    x_min, y_min, x_max, y_max = bounds
    fig = Figure()
    ax = fig.add_subplot(111)
    ax.set_ylim(y_min - 1, y_max + 1)
    ax.set_xlim(x_min - 1, x_max + 1)

    n = len(list(polygons))
    if fillcolors is None:
        fillcolors = ['#6b6b32'] * n

    if linecolors is None:
        linecolors = ['#fff'] * n

    for i in range(n):
        displayPolygon(polygons[i], ax, filename=filename, fillcolor=fillcolors[i], linecolor=linecolors[i])

    if filename is None:
        plt.show()
    else:
        # plt.savefig(filename)
        canvas = FigureCanvasAgg(fig)
        canvas.print_figure(filename, dpi=100)


def hexagonal_lattice(rows=3, cols=3, noise=0.0):
    """
    Generates mxn heaxgonal lattice. Noise determines the noisiness to be applied to perturb
    the grid.
    Returnd coordinates of the centroids of hexagons
    """
    # Assemble a hexagonal lattice

    rows = int(rows)
    cols = int(cols)
    noise = float(noise)

    points = []
    for row in range(rows * 2):
        for col in range(cols):
            x = (col + (0.5 * (row % 2))) * np.sqrt(3)
            y = row * 0.5
            points.append((x, y, 0))
    points = np.asarray(points)
    points += np.random.multivariate_normal(mean=np.zeros(3) - 0.04, cov=np.eye(3) * noise, size=points.shape[0])
    # Set z=0 again for all points after adding Gaussian noise
    points[:, 2] = 0

    return points


def def_val():
    '''
    default value for the deafultdict. Only a helper function
    '''
    return []


colors = {
    'grassland': ['#ccd4bb', '#c4ccbb', '#e4e8ca'],
    'building': ['#bbbbbb', '#aaaaaa', '#999999'],  # OR desserts/peninsula
    'waterbody': ['#0247cd', '#064bcc', '#0d51d1'],
    'ocean': ['#012b78', '#033591', '#02379c'],
    'mountain': ['#f8f8f8', '#ebebeb', '#e8e8e8'],
    'forest': ['#9cbba9', '#a9cca4', '#c4d4aa'],
}

biomes = ['grassland', 'building', 'waterbody', 'ocean', 'mountain', 'forest']


def pick_biome(biomes, biome_dist):
    # print("picked biome from ", biomes, "with dist as\n", biome_dist)
    return np.random.choice(biomes, p=biome_dist)


# shift probabilty away from the darker colors towards lighter colors
def update_prob_dist(dist, update):
    '''
    takes in a probably distribution and applies updates to it
    '''
    if dist[0] < -1 * update[0]:
        return dist
    return dist + update


def setBoundingOcean(multipolygon, boundary, bounds, cmap, buffer=0.01, noise=0.03):
    '''
    Returns a multipolygon consisting of all polygons that lie in a buffer around the boundary
    '''
    x_max, x_min = bounds
    width = (x_max - x_min)
    for i in range(len(list(multipolygon))):
        ocean = boundary.buffer((buffer + np.random.uniform(high=noise)) * width)
        if multipolygon[i].representative_point().within(ocean):
            cmap[i] = colors['ocean'][0]


def combine_polys(multi, biome_dist, comb_max=100):
    """
    randomly clusters hexagons together into more complicated polygons consisting
    upto comb_max hexagons.

    """
    G = Graph()
    G.make_graph_from_multipolygon(multi)
    cmap = [""] * G.n_vertices

    polygons = []
    while G.n_vertices:
        combined = set()
        adjacent = set()

        to_remove = choice(tuple(G.adj_list.keys()))
        combined.add(to_remove)

        for adj in G.adj_list[to_remove]:
            adjacent.add(adj)

        G.remove(to_remove)

        biome = pick_biome(biomes, biome_dist)
        prob_dist = np.array([0.3, 0.45, 0.25])
        update = np.array([-0.01, -0.01, 0.02])
        cmap[to_remove] = colors[biome][np.random.choice(a=[0, 1, 2], p=prob_dist)]
        prob_dist = update_prob_dist(prob_dist, update)

        for _ in range(np.random.randint(comb_max)):
            if len(adjacent) == 0:
                break
            to_remove = choice(tuple(adjacent))
            adjacent.remove(to_remove)
            combined.add(to_remove)

            cmap[to_remove] = colors[biome][np.random.choice([0, 1, 2], p=prob_dist)]
            prob_dist = update_prob_dist(prob_dist, update)

            for adj in G.adj_list[to_remove]:
                adjacent.add(adj)
            G.remove(to_remove)
        polygons.append(MultiPolygon([multi[i] for i in combined]))
    del polygons
    return cmap
