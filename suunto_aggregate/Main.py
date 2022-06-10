import random
import csv
import os
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk

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


def parse_files(filenames, min_depth, auto_zero):
    plots = []
    max_duration = 0
    for file_path in filenames:
        full_file = xmltodict.parse(open(file_path, "r").read())
        header = full_file['sml']['DeviceLog']['Header']
        samples = full_file['sml']['DeviceLog']['Samples']
        del full_file

        max_duration = max(int(header['Duration']), max_duration)
        intervals = int(header['SampleInterval'])

        if float(header['Depth']['Max']) > min_depth:
            time = []
            depth = []
            data = []

            if auto_zero:
                time.append(0)
                depth.append(0)
                data.append({'time': 0, 'depth': 0})

            for sample in samples['Sample']:
                if 'Depth' not in sample:
                    pass
                else:
                    current_time = int(sample['Time'])
                    if auto_zero:
                        current_time += intervals
                    time.append(current_time)
                    depth.append(float(sample['Depth']))
                    data.append({'time': current_time, 'depth': float(sample['Depth'])})

            if auto_zero:
                depth.append(0)
                time.append(current_time + intervals)

            plots.append({"time": time, "depth": depth})
            export_datas.append(data)

    end = max_duration
    if auto_zero:
        end += intervals * 2

    annotations = {'start': 0, 'middle' : end/2, 'end': end}

    return plots, annotations


def make_plot(filenames, min_depth, auto_zero):
    fig = Figure(figsize=(16, 6.8), dpi=100)
    plot = fig.add_subplot(111)

    (plots, annotations) = parse_files(filenames, min_depth, auto_zero)

    for plot_data in plots:
        plot_data.setdefault('color', random_color())
        plot.plot(plot_data['time'], plot_data['depth'], plot_data['color'])

    plot.set_xlabel("Time (s)")
    plot.set_ylabel("Depth (m)")
    plot.invert_yaxis()

    plot.hlines(0, annotations['start'], annotations['end'],  linestyles='dashed', colors="blue")
    plot.text(annotations['middle'], -0.2, 'Surface', horizontalalignment='center', color='blue')

    if '!canvas' in root.children:
        root.children['!canvas'].destroy()
        root.children['!navigationtoolbar2tk'].destroy()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas.get_tk_widget().pack()

def is_entry_numeric(input):
    if input.isnumeric():
        return True
    elif input == "":
        return False
    else:
        return False


def launch_plot(filenames, min_depth, auto_zero=False):
    menu.entryconfig("Export to csv", state="normal")
    make_plot(filenames, min_depth, auto_zero)


def create_popup(filenames):
    top = tk.Toplevel(root)
    top.geometry("400x100")
    l = ttk.Label(top, text="Min depth filter")
    l.pack()
    e = ttk.Entry(top)
    reg = top.register(is_entry_numeric)
    e.config(validate="key", validatecommand=(reg, '%P'), takefocus=True)
    e.pack()
    chkValue = tk.BooleanVar()
    chkValue.set(True)
    c = ttk.Checkbutton(top, text="Active auto fill (Surface)", var=chkValue)
    c.pack()
    b = ttk.Button(top, text="Submit", command=lambda: [launch_plot(filenames, int(e.get()), chkValue.get()), top.destroy()])
    b.pack()

def select_files():
    filetypes = (
        ('sml files', '*.sml'),
        ('All files', '*.*')
    )

    filenames = fd.askopenfilenames(
        title='Open files',
        initialdir='/',
        filetypes=filetypes)
    create_popup(filenames)


def select_dest_dir():
    dirname = fd.askdirectory(
        title="Select directory",
        initialdir='/'
    )
    print(dirname)
    export_file = os.path.join(dirname, 'export.csv')
    with open(export_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for data in export_datas:
            writer.writerows(data)

# create the root window
root = tk.Tk()
root.title('Dive aggregator')
root.resizable(False, False)
root.geometry('1280x720')

menu = tk.Menu(root)
menu.add_command(label="Select Files", command=select_files)
menu.add_command(label="Export to csv", command=select_dest_dir, state="disabled")
root.config(menu=menu)
root.mainloop()
