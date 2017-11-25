from __future__ import absolute_import, division, print_function



"""Declare any extra link functions like this"""
#@link_function(info='translates A to B', output_labels=['b'])
#def a_to_b(a):
#    return a * 3
from glue.config import link_function

@link_function(info="Celsius to Fahrenheit", output_labels=['F'])
def celsius2farhenheit(c):
    return c  * 9. / 5. + 32

"""Data factories take a filename as input and return a Data object"""
#@data_factory('JPEG Image')
#def jpeg_reader(file_name):
#    ...
#    return data


"""Extra qt clients"""
#qt_client(ClientClass)

from glue import custom_viewer

from matplotlib.colors import LogNorm

bball = custom_viewer('Shot Plot',
                      x='att(x)',
                      y='att(y)')


@bball.plot_data
def show_hexbin(axes, x, y):
    axes.hexbin(x, y,
                cmap='Purples',
                gridsize=40,
                norm=LogNorm(),
                mincnt=1)


@bball.plot_subset
def show_points(axes, x, y, style):
    axes.plot(x, y, 'o',
              alpha=style.alpha,
              mec=style.color,
              mfc=style.color,
              ms=style.markersize)
