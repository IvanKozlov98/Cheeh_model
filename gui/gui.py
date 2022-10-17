import time
from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter.ttk import Notebook, Style
from tkinter.font import Font
from tkinter import filedialog
import numpy as np
from util.util import *

import matplotlib
import os.path
import matplotlib.pyplot as plt

matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import datetime



class GuiApp(tk.Tk):

    def __init__(self, controller):
        super(GuiApp, self).__init__()
        #
        self.HEIGHT = 700
        self.WIDTH = 1200
        self.controller = controller
        self.model = None
        self.thread = None  # for run Model
        # gui parameters
        self.tab_epidemic = None
        ##
        self.virus_params = dict()
        self.city_params = dict()
        self.model_params = dict()

        self.mild_thr = None
        self.start_thr = None
        self.severe_thr = None
        self.dead_thr = None
        self.spread_rate = None
        self.heavy_mort_rate = None
        self.mild_mort_rate = None
        self.initial_infected_people_count = None

        ###############
        self.population_count = None
        self.city_name = None

        ###############

        self.days_count = None

        self.initialize()

    @staticmethod
    def _create_spin(tab, text, column, row, from_=0.0, to=1.0, increment=0.01, string_var=None):
        w = Label(tab, text=text, fg="navyblue", font="50", background="white")
        w.grid(column=column, row=row)
        spin = Spinbox(tab, from_=from_, to=to, increment=increment, width=10,
                       font=Font(family='Helvetica', size=30, weight='bold'), textvariable=string_var)
        spin.grid(column=column, row=row + 1)
        return spin

    def save_configs(self):
        f = filedialog.askdirectory()
        time_raw = str(datetime.datetime.now())
        time_str = time_raw.replace(':', '_').replace('.', '_').replace(' ', '_')
        virus_config = os.path.join(f, f'virus_{time_str}.ini')
        model_config = os.path.join(f, f'model_{time_str}.ini')
        city_config = os.path.join(f, f'city_{time_str}.ini')
        self.validate_params()
        self.controller.save_config(virus_config, self.get_virus_params(), 'Virus')
        self.controller.save_config(model_config, self.get_model_params(), 'Model')
        self.controller.save_config(city_config, self.get_city_params(), 'City')


    def notify(self):
        ...

    def clear_graph(self):
        self.figure = Figure(figsize=(5, 4), dpi=170)
        self.plot = self.figure.add_subplot(1, 1, 1)
        self.plot.plot([], [])
        self.canvas = FigureCanvasTkAgg(self.figure, self.tab_epidemic)
        self.canvas.get_tk_widget().grid(row=0, column=0)
        self.figure.canvas.draw()

    def stop_program(self):
        self.controller.stop()

    def update(self):
        # self.figure = Figure(figsize=(5, 4), dpi=170)
        # self.plot = self.figure.add_subplot(1, 1, 1)
        times = np.arange(len(self.model.get_model_stats().list_number_new_infected_people))
        self.plot.plot(times, self.model.get_model_stats().list_number_new_infected_people, label="number new infected people")
        self.plot.plot(times, self.model.get_model_stats().list_number_recovered_people, label="number recovered people")
        self.plot.plot(times, self.model.get_model_stats().list_number_all_infected_people, label="number all infected people")
        self.plot.plot(times, self.model.get_model_stats().list_dead_people, label="number dead people")
        self.canvas = FigureCanvasTkAgg(self.figure, self.tab_epidemic)
        self.canvas.get_tk_widget().grid(row=0, column=0)
        self.figure.canvas.draw()


    def validate_params(self):
        ...

    def get_virus_params(self):
        virus_params = dict()
        virus_params["VIR_LOAD_THRESHOLD"] = self.start_thr.get()
        virus_params["MILD_THRESHOLD"] = self.mild_thr.get()
        virus_params["SEVERE_THRESHOLD"] = self.severe_thr.get()
        virus_params["DEAD_THRESHOLD"] = self.dead_thr.get()
        virus_params["SPREAD_RATE"] = self.spread_rate.get()
        virus_params["HEAVY_MORT_RATE"] = self.heavy_mort_rate.get()
        virus_params["MILD_MORT_RATE"] = self.mild_mort_rate.get()
        return virus_params

    def get_city_params(self):
        city_params = dict()
        city_params["POPULATION_COUNT"] = self.population_count.get()
        city_params["NAME_LOCATION"] = self.city_name.get()
        return city_params

    def get_model_params(self):
        model_params = dict()
        model_params["INITIAL_INFECTED_PEOPLE_COUNT"] = self.initial_infected_people_count.get()
        model_params["DAYS_COUNT"] = self.days_count.get()
        return model_params

    def my_program(self):
        global thread
        self.validate_params()
        self.time_array = np.arange(int(self.days_count.get()))
        ################
        virus_params = self.get_virus_params()
        city_params = self.get_city_params()
        model_params = self.get_model_params()
        #
        # start program
        self.model = self.controller.create_model(model_config=model_params, city_config=city_params,
                                                  virus_config=virus_params, view=self)
        self.thread = threading.Thread(target=self.model.run)
        self.thread.daemon = True
        self.thread.start()

    def initialize(self):
        self.title('Cheeh model')
        # Adjust size
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        # set minimum window size value
        self.minsize(self.WIDTH, self.HEIGHT)
        # set maximum window size value
        self.maxsize(self.WIDTH, self.HEIGHT)

        # frames to store separators with different geometry managers
        frame1 = Frame(self)
        frame1.pack(side=LEFT, expand=True, fill=BOTH)

        self.frame2 = Frame(self)
        self.frame2.pack(side=LEFT, expand=True, fill=BOTH)



        Mysky = "#DCF0F2"
        Myyellow = "#F2C84B"

        style = Style()

        style.theme_create("dummy", parent="alt", settings={
            "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0]}},
            "TNotebook.Tab": {
                "configure": {"padding": [5, 1], "background": Mysky},
                "map": {"background": [("selected", Myyellow)],
                        "expand": [("selected", [1, 1, 1, 0])]}}})
        style.theme_use("dummy")

        tab_control = ttk.Notebook(frame1)
        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)
        tab3 = ttk.Frame(tab_control)
        tab_control.add(tab1, text='Model parameters')
        tab_control.add(tab2, text='Virus parameters')
        tab_control.add(tab3, text='City parameters')

        #
        bg = tk.PhotoImage(file="data/img/virus.png")

        # Model
        label1 = Label(tab1, image=bg)
        label1.photo = bg
        label1.place(x=0, y=0, relwidth=1, relheight=1)

        self.initial_infected_people_count_var = StringVar()
        self.initial_infected_people_count = self._create_spin(tab1, "Initial infected people count", 0, 0, from_=100,
                                                               to=100000, increment=100, string_var=self.initial_infected_people_count_var)
        self.days_count_var = StringVar()
        self.days_count = self._create_spin(tab1, "Days count", 0, 2, from_=10, to=1000, increment=20, string_var=self.days_count_var)

        # Virus
        label2 = Label(tab2, image=bg)
        label2.place(x=0, y=0)

        self.start_thr_var = StringVar()
        self.mild_thr_var = StringVar()
        self.severe_thr_var = StringVar()
        self.dead_thr_var = StringVar()
        self.spread_rate_var = StringVar()
        self.heavy_mort_rate_var = StringVar()
        self.mild_mort_rate_var = StringVar()

        # scrollbar = Scrollbar(tab2)
        # scrollbar.pack(side=RIGHT, fill=Y)
        # mylist = Listbox(tab2, yscrollcommand=scrollbar.set)
        # for line in range(100):
        #     mylist.insert(END, "This is line number " + str(line))
        #
        # mylist.pack(side=LEFT, fill=BOTH)
        # scrollbar.config(command=mylist.yview)

        self.start_thr = self._create_spin(tab2, "Start threshold", 0, 0, string_var=self.start_thr_var)
        self.mild_thr = self._create_spin(tab2, "Mild threshold", 0, 2, string_var=self.mild_thr_var)
        self.severe_thr = self._create_spin(tab2, "Severe threshold", 0, 4, string_var=self.severe_thr_var)
        self.dead_thr = self._create_spin(tab2, "Dead threshold", 0, 6, string_var=self.dead_thr_var)
        self.spread_rate = self._create_spin(tab2, "Spread rate", 0, 8, string_var=self.spread_rate_var)
        self.heavy_mort_rate = self._create_spin(tab2, "Heavy mortality rate", 0, 10, string_var=self.heavy_mort_rate_var)
        self.mild_mort_rate = self._create_spin(tab2, "Mild mortality rate", 0, 12, string_var=self.mild_mort_rate_var)

        # City
        label3 = Label(tab3, image=bg)
        label3.place(x=0, y=0)

        self.population_count_var = StringVar()
        self.population_count = self._create_spin(tab3, "Population count", 0, 0,
                                                  from_=1000, to=1000000, increment=1000,
                                                  string_var=self.population_count_var)
        self.city_name_var = StringVar()

        w = Label(tab3, text="Name of city", fg="navyblue", font="50", background="white")
        w.grid(column=0, row=2)
        self.city_name = Entry(tab3, width=10, font=Font(family='Helvetica', size=30, weight='bold'), textvariable=self.city_name_var)
        self.city_name.grid(column=0, row=3)

        #########################################



        self.tab_control_vis = ttk.Notebook(self.frame2)
        self.tab_epidemic = ttk.Frame(self.tab_control_vis)
        self.tab2_ = ttk.Frame(self.tab_control_vis)
        self.tab3_ = ttk.Frame(self.tab_control_vis)
        self.tab_control_vis.add(self.tab_epidemic, text='Epidemic dynamic')
        self.tab_control_vis.add(self.tab2_, text='Todo1')
        self.tab_control_vis.add(self.tab3_, text='Todo2')

        self.tab_control_vis.pack(expand=1, fill='both')
        #########################################

        self.figure = Figure(figsize=(5, 4), dpi=170)
        self.plot = self.figure.add_subplot(1, 1, 1)
        self.plot.plot([], [], color="blue", marker="x", linestyle="")
        self.canvas = FigureCanvasTkAgg(self.figure, self.tab_epidemic)
        self.canvas.get_tk_widget().grid(row=0, column=0)

        #########################################

        frameBottom = Frame(frame1)
        frameBottom.pack(side=BOTTOM)

        runbutton = Button(frameBottom, text="Run!", fg="black", command=self.my_program)
        runbutton.pack(side=LEFT)

        stopButton = Button(frameBottom, text="Stop!", fg="black", command=self.stop_program)
        stopButton.pack(side=LEFT)

        saveConfigButton = Button(frameBottom, text="Save configs", fg="black", command=self.save_configs)
        saveConfigButton.pack(side=RIGHT)

        clearButton = Button(frameBottom, text="Clear graph", fg="black", command=self.clear_graph)
        clearButton.pack(side=RIGHT)

        ####
        tab_control.pack(expand=1, fill='both')


        def load_city_config_impl(file):
            self.population_count_var.set(get_value_from_config(file, "City", "POPULATION_COUNT"))
            self.city_name_var.set(get_value_from_config(file, "City", "NAME_LOCATION"))

        def load_model_config_impl(file):
            self.initial_infected_people_count_var.set(get_value_from_config(file, "Model", "INITIAL_INFECTED_PEOPLE_COUNT"))
            self.days_count_var.set(get_value_from_config(file, "Model", "DAYS_COUNT"))

        def load_virus_config_impl(file):
            self.start_thr_var.set(get_value_from_config(file, "Virus", "VIR_LOAD_THRESHOLD"))
            self.mild_thr_var.set(get_value_from_config(file, "Virus", "MILD_THRESHOLD"))
            self.severe_thr_var.set(get_value_from_config(file, "Virus", "SEVERE_THRESHOLD"))
            self.dead_thr_var.set(get_value_from_config(file, "Virus", "DEAD_THRESHOLD"))
            self.spread_rate_var.set(get_value_from_config(file, "Virus", "SPREAD_RATE"))
            self.heavy_mort_rate_var.set(get_value_from_config(file, "Virus", "HEAVY_MORT_RATE"))
            self.mild_mort_rate_var.set(get_value_from_config(file, "Virus", "MILD_MORT_RATE"))


        def load_model_config():
            file = filedialog.askopenfilename(filetypes = (("Config files", "*.ini"),("all files", "*.*")))
            load_model_config_impl(file)

        def load_city_config():
            file = filedialog.askopenfilename(filetypes = (("Config files", "*.ini"),("all files", "*.*")))
            load_city_config_impl(file)

        def load_virus_config():
            file = filedialog.askopenfilename(filetypes = (("Config files", "*.ini"),("all files", "*.*")))
            load_virus_config_impl(file)
        # menu
        menu = Menu(self)
        new_item = Menu(menu)
        new_item.add_command(label='Load model parameters', command=load_model_config)
        new_item.add_command(label='Load virus parameters', command=load_virus_config)
        new_item.add_command(label='Load city parameters', command=load_city_config)
        menu.add_cascade(label='File', font=("Helvetica", "16"), menu=new_item)
        self.config(menu=menu)
        ##########################################
        # set default values
        load_city_config_impl("config/cities/Voronesh.ini")
        load_model_config_impl("config/model/model.ini")
        load_virus_config_impl("config/viruses/covid-19.ini")

    def run(self):
        self.mainloop()
