'''
Present an interactive function explorer with slider widgets.

Scrub the sliders to change the properties of the ``sin`` curve, or
type into the title text box to update the title of the plot.

Use the ``bokeh serve`` command to run the example by executing:

    bokeh serve sliders.py

at your command prompt. Then navigate to the URL

    http://localhost:5006/sliders

in your browser.
'''

import configparser
import itertools
import numpy as np
from scipy.stats import beta
config = configparser.ConfigParser()
config.read('config')

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, TextInput
from bokeh.plotting import figure

def getAlphaBeta(mu, sigma):
    alpha = mu**2 * ((1 - mu) / sigma**2 - 1 / mu)
    beta = alpha * (1 / mu - 1)
    return {"alpha": alpha, "beta": beta}

def virus_count(days, repro_rate, vir_count_0, lag, a_shape_distrib_nespecific_param, b_shape_distrib_nespecific_param, a_shape_distrib_specific_param, b_shape_distrib_specific_param):
    res_list = []
    res_spec_immun_list = []

    alphabeta_shape_distrib_specific_param = getAlphaBeta(a_shape_distrib_specific_param, b_shape_distrib_specific_param)
    alphabeta_shape_distrib_nonspecific_param = getAlphaBeta(a_shape_distrib_nespecific_param, b_shape_distrib_nespecific_param)
    print(alphabeta_shape_distrib_specific_param)
    print(alphabeta_shape_distrib_nonspecific_param)


    alfa = np.array(beta.rvs(size=people_count, a=alphabeta_shape_distrib_specific_param['alpha'], b=alphabeta_shape_distrib_specific_param['beta']))/norm_alfa_coef #alfa/norm_alfa_coef
    unspec_immun = beta.rvs(size=people_count, a=alphabeta_shape_distrib_nonspecific_param['alpha'], b=alphabeta_shape_distrib_nonspecific_param['beta'])
    spec_immun = 0

    for pers in range(people_count):
        sub_list = []
        sub_spec_immun_list = []
        y = vir_count_0
        sub_list.append(y)
        spec_immun = 0
        for day in range(days):
            if day > lag:
                spec_immun = np.arctan(sub_list[-lag]*alfa[pers] + spec_immun) #*2/np.pi
            # print(spec_immun)
            y += y * repro_rate
            y *= (1 - unspec_immun[pers]) * (1 - spec_immun/1.57)
            # print(y)
            sub_list.append(y)
            sub_spec_immun_list.append(spec_immun)
        res_list.append(sub_list)
        res_spec_immun_list.append(sub_spec_immun_list)
    return res_list, res_spec_immun_list



# Set up data
DAYS_CONST = int(config.get('DEFAULT', 'DAYS'))
x = range(DAYS_CONST)
people_count = 20

vir_count_0_const = 100
repro_rate_const = 0.2
# unspec_immun_const = 1.0
norm_alfa_coef = 1000
# alfa_const = 0
lag_const = 5
vir_count_limit = 500
a_shape_distrib_nespecific_param_const = 0.2
b_shape_distrib_nespecific_param_const = 0.1
a_shape_distrib_specific_param_const = 0.2
b_shape_distrib_specific_param_const = 0.1

y, spec_immun = virus_count(DAYS_CONST,
                            repro_rate_const,
                            # unspec_immun_const,
                            vir_count_0_const,
                            # alfa_const,
                            lag_const,
                            a_shape_distrib_nespecific_param_const,
                            b_shape_distrib_nespecific_param_const,
                            a_shape_distrib_specific_param_const,
                            b_shape_distrib_specific_param_const
                            ) # virus count

source_data_dict = {str('x'):x}
for pers in range(people_count):
    source_data_dict.update({str(f'y{pers}'): y[pers], str(f'C_t{pers}'): list(np.array(spec_immun[pers]) * vir_count_limit/1.57)})
source = ColumnDataSource(data=source_data_dict)


# Set up plot
plot = figure(height=600, width=600, title="Virus count",
              tools="crosshair,pan,reset,save,wheel_zoom",
              x_range=[0, DAYS_CONST], y_range=[0, vir_count_limit])


for pers in range(people_count):
    plot.line('x', f'y{pers}', source=source, line_width=1, line_alpha=0.4, color="green", legend="Count of virus, N_t") #legend_group="Count of virus, N_t",
    plot.line('x', f'C_t{pers}', source=source, line_width=1, line_alpha=0.4, color="red", legend="Specific immun, C_t") #legend_group="Specific immun, C_t",

# Set up widgets
text = TextInput(title="title", value='Virus count')
repro_rate = Slider(title="Reproduction rate", value=repro_rate_const, start=0, end=1, step=0.1)
# unspec_immun = Slider(title="unspec_immun", value=unspec_immun_const, start=0, end=1, step=0.1)
# alfa = Slider(title=f"alfa/{norm_alfa_coef}", value=alfa_const, start=0, end=1, step=0.0001)
lag = Slider(title="Lag in days", value=lag_const, start=0, end=10, step=1)
vir_count_0 = Slider(title="Virus count, 1 day", value=vir_count_0_const, start=0, end=300, step=20)
a_shape_distrib_nespecific_param = Slider(title="Non specific immun, mean", value=a_shape_distrib_nespecific_param_const, start=0, end=1, step=0.01)
b_shape_distrib_nespecific_param = Slider(title="Non specific immun, sigma", value=b_shape_distrib_nespecific_param_const, start=0, end=1, step=0.01)
a_shape_distrib_specific_param = Slider(title="Specific immun, mean", value=a_shape_distrib_specific_param_const, start=0, end=1, step=0.01)
b_shape_distrib_specific_param = Slider(title="Specific immun, sigma", value=b_shape_distrib_specific_param_const, start=0, end=1, step=0.01)


# Set up callbacks
def update_title(attrname, old, new):
    plot.title.text = text.value

text.on_change('value', update_title)

def update_data(attrname, old, new):

    # Get the current slider values
    repro_rate_loc = repro_rate.value
    # unspec_immun_loc = unspec_immun.value
    # alfa_loc = alfa.value
    lag_loc = lag.value
    vir_count_0_loc = vir_count_0.value
    a_shape_distrib_specific_param_loc = a_shape_distrib_specific_param.value
    b_shape_distrib_specific_param_loc = b_shape_distrib_specific_param.value
    a_shape_distrib_nespecific_param_loc = a_shape_distrib_nespecific_param.value
    b_shape_distrib_nespecific_param_loc = b_shape_distrib_nespecific_param.value

    # Generate the new curve
    x = range(DAYS_CONST)
    y, spec_immun = virus_count(DAYS_CONST,
                                repro_rate_loc,
                                # unspec_immun_loc,
                                vir_count_0_loc,
                                # alfa_loc,
                                lag_loc,
                                a_shape_distrib_nespecific_param_loc,
                                b_shape_distrib_nespecific_param_loc,
                                a_shape_distrib_specific_param_loc,
                                b_shape_distrib_specific_param_loc)
    source_data_dict = {str('x'):x}
    for pers in range(people_count):
        source_data_dict.update(
            {str(f'y{pers}'): y[pers], str(f'C_t{pers}'): list(np.array(spec_immun[pers]) * vir_count_limit / 1.57)})
    source.data = source_data_dict

for w in [repro_rate, vir_count_0, lag, a_shape_distrib_nespecific_param, b_shape_distrib_nespecific_param, a_shape_distrib_specific_param, b_shape_distrib_specific_param]:
    w.on_change('value', update_data)


# Set up layouts and add to document
inputs = column(text, repro_rate, vir_count_0, lag, vir_count_0, a_shape_distrib_nespecific_param, b_shape_distrib_nespecific_param, a_shape_distrib_specific_param, b_shape_distrib_specific_param)

curdoc().add_root(row(inputs, plot, width=800))
curdoc().title = "Sliders"
