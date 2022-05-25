import random
import csv
import os
import tkinter as tk
from tkinter import filedialog as fd

import matplotlib.colors as mcolors
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import xmltodict

color_list = list(mcolors.XKCD_COLORS.keys())

CSV_FIELDS = ['time', 'depth']
export_datas = []


def random_color():
    color = random.choice(color_list)
    color_list.remove(color)
    return color


def make_plot(files):
    fig = Figure(figsize=(16, 6.8), dpi=100)
    plot = fig.add_subplot(111)
    for file_path in files:
        full_file = xmltodict.parse(open(file_path, "r").read())
        header = full_file['sml']['DeviceLog']['Header']
        samples = full_file['sml']['DeviceLog']['Samples']
        del full_file

        if float(header['Depth']['Max']) > 2:
            time = [0]
            depth = [0]
            data = [{'time': 0, 'depth': 0}]
            for sample in samples['Sample']:
                if int(sample['Time']) == 0 and 'Depth' not in sample:
                    pass
                else:
                    current_time = int(sample['Time']) + 2
                    time.append(current_time)
                    depth.append(float(sample['Depth']))
                    data.append({'time': current_time, 'depth': float(sample['Depth'])})
            plot.plot(time, depth, random_color())
            export_datas.append(data)

    plot.set_xlabel("Time (s)")
    plot.set_ylabel("Depth (m)")
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas.get_tk_widget().pack()


# create the root window
root = tk.Tk()
root.title('Dive aggregator')
root.resizable(False, False)
root.geometry('1280x720')


def select_files():
    filetypes = (
        ('text files', '*.xml'),
        ('All files', '*.*')
    )

    filenames = fd.askopenfilenames(
        title='Open files',
        initialdir='/',
        filetypes=filetypes)
    make_plot(filenames)


def select_dest_dir():
    dirname = fd.askdirectory(
        title="Select directory",
        initialdir='/'
    )
    print(dirname)
    export_file = os.path.join(dirname, 'export.csv')
    with open(export_file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for data in export_datas:
            writer.writerows(data)


menu = tk.Menu(root)
menu.add_command(label="Select Files", command=select_files)
menu.add_command(label="Export to csv", command=select_dest_dir)
root.config(menu=menu)
root.mainloop()
