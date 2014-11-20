from matplotlib import pyplot, cm
import matplotlib.colors as colors
import mpl_toolkits.mplot3d.art3d as art3d
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from numpy import ndarray

from descartes import PolygonPatch

from neighborhood_loader import *
from query_neighborhoods import *


def draw_hoods(boroughs, dataset):
    if dataset != "pickups" and dataset != "drops":
        raise Exception("Error: the two datasets are 'pickups' and "
                        "'drops', not ", str(dataset))

    datafile = 'neighborhoods/nyc-pediacities-neighborhoods-v3-polygon.geojson'
    hoodlist = parse_neighborhood_file(datafile)
    xlim = len(boroughs) == 5
    f1 = 15 if len(boroughs) == 5 else 10

    fig = pyplot.figure(1, figsize=(f1, 10))

    myplot = fig.add_subplot(111)

    if xlim:
        myplot.set_xlim(-74.35, -73.6)
        myplot.set_ylim(40.45, 40.95)

    hood_count, maxes, mins = load_precomputed_count(boroughs)
    if mins[dataset] == 0:
        mins[dataset] = 1
    norm = colors.LogNorm(mins[dataset], maxes[dataset])

    for n in hoodlist.keys():

        # keep it to requested boroughs
        if hoodlist[n]["boroughCode"] not in boroughs:
            continue

        count = hood_count[n][dataset]
        color = colors.rgb2hex(cm.OrRd(norm(count)))

        if hoodlist[n]["location"]["type"] == "MultiPolygon":
            for c in hoodlist[n]["location"]["coordinates"]:
                patch = PolygonPatch({"type": "Polygon", "coordinates": c},
                                     fc=color, ec='#000000', alpha=1.0,
                                     zorder=2)
                myplot.add_patch(patch)

        else:
            patch = PolygonPatch(hoodlist[n]["location"],
                                 fc=color, ec="#000000", alpha=1.0, zorder=2)
            myplot.add_patch(patch)

    if not xlim:
        myplot.relim()
        myplot.autoscale_view()

    filename = ''.join(str(b) for b in boroughs)
    pyplot.savefig(filename + dataset + '.png', bbox_inches='tight', dpi=100)


def plot_timeVfreq(date_operator, DB):
    tvf = get_timeVfreq(date_operator, DB[0], DB[1])

    min_freq = ndarray.min(tvf[1])
    max_freq = ndarray.max(tvf[1])

    fig = pyplot.figure(1, figsize=(20, 6))
    myplot = fig.add_subplot(111)
    myplot.set_xlim(1, 366)
    print "min=" + str(min_freq) + ", max=" + str(max_freq)
    norm = colors.Normalize(min_freq, max_freq)

    for i in range(len(tvf[0])):
        color = colors.rgb2hex(cm.cool(norm(tvf[1][i])))
        pyplot.bar(tvf[0][i], tvf[1][i], color=color, ec=color, align='edge')

    pyplot.xlabel(date_operator)
    pyplot.ylabel("# of rides")
    pyplot.show()
    pyplot.savefig(q + "_" + DB[0], dpi=180)


def draw_hoods3D(boroughs, dataset):
    if dataset != "pickups" and dataset != "drops":
        raise Exception("Error: the two datasets are 'pickups' "
                        "and 'drops', not ", str(dataset))

    datafile = 'neighborhoods/nyc-pediacities-neighborhoods-v3-polygon.geojson'
    hoodlist = parse_neighborhood_file(datafile)
    manhattan = len(boroughs) == 1 and boroughs[0] == 1
    nyc = len(boroughs) == 5

    fig = pyplot.figure(1, figsize=(7, 6))
    ax = fig.gca(projection='3d')

    if manhattan:
        ax.set_xlim3d(-74.07, -73.85)
        ax.set_ylim3d(40.65, 40.90)
    elif nyc:
        ax.set_xlim3d(-74.35, -73.6)
        ax.set_ylim3d(40.45, 40.95)

    hood_count, maxes, mins = load_precomputed_count(boroughs)
    if mins[dataset] == 0:
        mins[dataset] = 100
    norm = colors.LogNorm(mins[dataset], maxes[dataset])

    for n in hoodlist.keys():

        # keep it to requested boroughs
        if hoodlist[n]["boroughCode"] not in boroughs:
            continue

        count = hood_count[n][dataset]
        if norm(count) < 0:
            count = 0
        rgba = cm.OrRd(norm(count))
        color = colors.rgb2hex(rgba)
        tint = colors.rgb2hex((rgba[0] * 0.9, rgba[1] * 0.9,
                               rgba[2] * 0.9, rgba[3] * 0.9))

        if hoodlist[n]["location"]["type"] == "MultiPolygon":
            for c in hoodlist[n]["location"]["coordinates"]:
                patch = PolygonPatch({"type": "Polygon", "coordinates": c},
                                     fc=color, ec=tint, alpha=1.0, zorder=2)
                ax.add_patch(patch)
                art3d.pathpatch_2d_to_3d(patch, z=norm(count), zdir='z')
                art3d.pathpatch_2d_to_3d(patch, z=0, zdir='z')

                num_coords = len(c[0])
                verts = []
                for i in range(num_coords):
                    P = c[0][i % num_coords]
                    Q = c[0][(i + 1) % num_coords]

                    x = [P[0], Q[0], Q[0], P[0]]
                    y = [P[1], Q[1], Q[1], P[1]]
                    z = [0, 0, norm(count), norm(count)]
                    verts.append(zip(x, y, z))

                coll = Poly3DCollection(verts)
                coll.set_facecolors(color)
                coll.set_edgecolors(tint)
                ax.add_collection3d(coll)

        else:
            patch = PolygonPatch(hoodlist[n]["location"], fc=color, ec=tint,
                                 alpha=1.0, zorder=2)
            ax.add_patch(patch)
            art3d.pathpatch_2d_to_3d(patch, z=norm(count), zdir='z')

            num_coords = len(hoodlist[n]["location"]["coordinates"][0])
            verts = []
            for i in range(num_coords):
                P = hoodlist[n]["location"]["coordinates"][0][i % num_coords]
                Q = hoodlist[n]["location"]["coordinates"][0][(i + 1) %
                                                              num_coords]

                x = [P[0], Q[0], Q[0], P[0]]
                y = [P[1], Q[1], Q[1], P[1]]
                z = [0, 0, norm(count), norm(count)]
                verts.append(zip(x, y, z))

            coll = Poly3DCollection(verts)
            coll.set_facecolors(color)
            coll.set_edgecolors(tint)
            ax.add_collection3d(coll)

    filename = ''.join(str(b) for b in boroughs)
    pyplot.savefig(filename + dataset + '.png', bbox_inches='tight', dpi=100)
