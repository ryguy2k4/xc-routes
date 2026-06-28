import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx

def plot_map(gdf, ax):
    gdf.to_crs(3857).plot(ax=ax)
    cx.add_basemap(ax, source=cx.providers.CartoDB.Voyager)
    ax.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)