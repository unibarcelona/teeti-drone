from __future__ import print_function

from tornado.ioloop import IOLoop
from bokeh.application.handlers import Handler
from bokeh.application import Application
from bokeh.server.server import Server
from bokeh.models import Slider
from bokeh.plotting import figure
from bokeh.driving import count
from bokeh.layouts import gridplot, column

import numpy as np
import pandas as pd
from gyro.device import Board


class GyroHandler(Handler):
    def __init__(self):
        super(GyroHandler, self).__init__()

        self.board = Board(firmware="teeti-MPU9250-firmware")
        print(self.board)
        # board.upload()

        self.board.connect()

    def modify_document(self, doc):

        plt_acc_x = figure(plot_width=400, plot_height=400, title="X-axis",
                           y_axis_label='G', x_axis_label='ms')
        plt_acc_y = figure(plot_width=400, plot_height=400, title="Y-axis",
                           y_axis_label='G', x_axis_label='ms')
        plt_acc_z = figure(plot_width=400, plot_height=400, title="Z-axis",
                           y_axis_label='G', x_axis_label='ms')

        line_acc_x = plt_acc_x.line(np.arange(100)*100, np.zeros(100), color="firebrick", line_width=2)
        plt_acc_x.line(np.arange(100)*100, np.zeros(100) + 1, color="black", line_width=1)
        plt_acc_x.line(np.arange(100)*100, np.zeros(100) - 1, color="black", line_width=1)

        line_acc_y = plt_acc_y.line(np.arange(100)*100, np.zeros(100), color="navy", line_width=2)
        plt_acc_y.line(np.arange(100)*100, np.zeros(100) + 1, color="black", line_width=1)
        plt_acc_y.line(np.arange(100)*100, np.zeros(100) - 1, color="black", line_width=1)

        line_acc_z = plt_acc_z.line(np.arange(100)*100, np.zeros(100), color="green", line_width=2)
        plt_acc_z.line(np.arange(100)*100, np.zeros(100) + 1, color="black", line_width=1)
        plt_acc_z.line(np.arange(100)*100, np.zeros(100) - 1, color="black", line_width=1)

        ds_acc_x = line_acc_x.data_source
        ds_acc_y = line_acc_y.data_source
        ds_acc_z = line_acc_z.data_source

        # window_size = 5

        # slider = Slider(start=0, end=25, value=window_size, step=1)
        #
        # doc.add_root(column(slider, the_plot))

        grid = gridplot([[plt_acc_x, plt_acc_y, plt_acc_z]], responsive=True)
        doc.add_root(grid)

        def update():

            updated_dataframe = self.board.read()

            # z = pd.Series.rolling(updated_dataframe["acc"]["z"], window=slider.value).mean()

            ds_acc_x.data['y'] = np.array(updated_dataframe["acc"]["x"])
            ds_acc_y.data['y'] = np.array(updated_dataframe["acc"]["y"])
            ds_acc_z.data['y'] = np.array(updated_dataframe["acc"]["z"])

            ds_acc_x.trigger('data', ds_acc_x.data, ds_acc_x.data)
            ds_acc_y.trigger('data', ds_acc_y.data, ds_acc_y.data)
            ds_acc_z.trigger('data', ds_acc_z.data, ds_acc_z.data)

        # Add a periodic callback to be run every 500 milliseconds
        doc.add_periodic_callback(update, 100)

io_loop = IOLoop.current()

bokeh_app = Application(GyroHandler())

server = Server({'/': bokeh_app}, io_loop=io_loop)
server.start()

if __name__ == '__main__':
    print('Opening Bokeh application on http://localhost:5006/')
    io_loop.add_callback(server.show, "/")
    io_loop.start()