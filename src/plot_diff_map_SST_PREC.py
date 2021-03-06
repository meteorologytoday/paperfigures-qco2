import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib as mplt
import matplotlib.ticker as mticker
from matplotlib import cm
import matplotlib.patches as patches

from quick_tools import *

import os

#mplt.use('Agg')

from matplotlib import rc

default_linewidth = 2.0;
default_ticksize = 10.0;

mplt.rcParams['lines.linewidth'] =   default_linewidth;
mplt.rcParams['axes.linewidth'] =    default_linewidth;
mplt.rcParams['xtick.major.size'] =  default_ticksize;
mplt.rcParams['xtick.major.width'] = default_linewidth;
mplt.rcParams['ytick.major.size'] =  default_ticksize;
mplt.rcParams['ytick.major.width'] = default_linewidth;

#rc('font', **{'family':'sans-serif', 'serif': 'Bitstream Vera Serif', 'sans-serif': 'MS Reference Sans Serif', 'size': 20.0});
rc('font', **{'size': 12.0});
rc('axes', **{'labelsize': 12.0});
rc('mathtext', **{'fontset':'stixsans'});
#rc(('xtick.major','ytick.major'), pad=20)

#import matplotlib.font_manager as fm;
#print("%s: %d"%(fm.FontProperties().get_name(),fm.FontProperties().get_weight()));

import matplotlib.pyplot as plt

import sys, argparse
from netCDF4 import Dataset
import numpy as np
from pprint import pprint


def ext(data):
    s = data.shape
    ndata = np.zeros((s[0], s[1]+1))
    ndata[:, 0:-1] = data
    ndata[:, -1] = data[:, 0]
    return ndata
 
def ext_axis(lon):
    return np.append(lon, 360) 

def area_mean(data, area):
    data.mask = False
    idx = np.isfinite(data)
    aa = area[idx]
    return sum(data[idx] * aa) / sum(aa)
 
domain_file = "CESM_domains/domain.lnd.fv0.9x1.25_gx1v6.090309.nc"

sim_var = getSimVars(["SST", "PREC_TOTAL"])
#sim_var = getSimVars(["TMXL", "XMXL"])

plot_cases = ["POP2_671-700", "POP2_571-600", "EMOM", "MLM", "SOM"]
plot_cases = ["POP2_671-700", "EMOM", "MLM", "SOM"]
#plot_cases = ["POP2_671-700",]
sim_casenames = getSimcases(plot_cases)


Re = 6371e3
with Dataset(domain_file, "r") as f:
    lat  = f.variables["yc"][:, 0]
    lon  = f.variables["xc"][0, :]
    dx = 2 * np.pi * np.cos(f.variables["yc"][:] * np.pi / 180.0) * Re / len(lon)
    mask = f.variables["mask"][:]
    area = f.variables["area"][:]
    llat  = f.variables["yc"][:]
    llon  = f.variables["xc"][:]
   

extrop_mask_idx = np.abs(llat) > 30.0
trop_mask_idx   = np.abs(llat) <= 30.0
lnd_mask_idx = (mask == 1.0)
ocn_mask_idx = (mask == 0.0)

data = {}

for scenario in ["CTL", "EXP"]:

    data[scenario] = {}

    for exp_name, caseinfo in sim_casenames.items():

        casename = caseinfo[scenario]
        data[scenario][exp_name] = {}
        
        for varname, filename  in sim_var.items():

            filename = "data/batch_diag/%s/%s" % (casename, filename, )
            
            with Dataset(filename, "r") as f:
                print("%s => %s" % (casename, varname))
                var_mean = "%s_MM" % varname
                var_std  = "%s_MASTD" % varname
                
                data[scenario][exp_name][var_mean] = f.variables[var_mean][:, 0, :, :]
                data[scenario][exp_name][var_std]  = f.variables[var_std][:, 0, :, :]





plot_infos = {
    "PREC_TOTAL" : {
        "display"   : "Precipitation rate",
        "unit"      : "[mm / day]",
        "cmap_mean" : "GnBu",
        "cmap_diff" : "BrBG",
        "clevels_obs"  : np.linspace(0, 10, 11),
        "clevels_diff" : np.linspace(-5, 5,  11),
        "clevels_diff_ticks" : np.linspace(-5, 5,  11),
        "factor"       : 86400.0 * 1000.0,
    },


    "SST" : {
        "display"   : "SST",
        "unit"      : "[degC]",
        "cmap_mean" : "gnuplot",
        "clevels_obs"  : np.linspace(-2, 30, 33),
        "clevels_diff" : np.linspace(-1, 1,  21),
        "clevels_diff_ticks" : np.linspace(-1, 1,  5),
        "factor"        : 1.0,
    },

    "PSL" : {
        "display"   : "SLP",
        "unit"      : "[hPa]",
        "cmap_mean" : "gnuplot",
        "clevels_obs"  : np.linspace(980, 1020, 11),
        "clevels_diff" : np.linspace(-1,   1, 11) * 10,
        "factor"       : 1e-2,
    },

    "HMXL" : {
        "display"   : "MLT",
        "unit"      : "[m]",
        "cmap_mean" : "GnBu",
        "clevels_obs"  : np.linspace(0, 300, 31),
        "clevels_diff" : np.linspace(-20, 20, 11),
        "factor"        : 1.0,
    },

    "XMXL" : {
        "display"   : "XMXL",
        "unit"      : "[m]",
        "cmap_mean" : "GnBu",
        "clevels_obs"  : np.linspace(0, 300, 31),
        "clevels_diff" : np.linspace(-20, 20, 11),
        "factor"        : 1.0,
    },


    "TMXL" : {
        "display"   : "TMXL",
        "unit"      : "[m]",
        "cmap_mean" : "GnBu",
        "clevels_obs"  : np.linspace(0, 300, 31),
        "clevels_diff" : np.linspace(-20, 20, 11),
        "factor"        : 1.0,
    },


    "aice" : {
        "display"   : "Sea-ice Concentration [%]",
        "unit"      : "[%]",
        "cmap_mean" : "GnBu",
        "clevels_obs"  : np.linspace(0, 100, 11),
        "clevels_diff" : np.linspace(-10,   10, 11),
        "factor"       : 1e2,
    },

    "STRAT" : {
        "display"   : r"$T_\mathrm{st}$",
        "unit"      : "[degC]",
        "cmap_mean" : "rainbow",
        "clevels_diff" : np.linspace(-2, 2,  11),
        "factor"        : 1.0,
    },


    "vice" : {
        "display"   : "SIT",
        "unit"      : "[m]",
        "cmap_mean" : "Blues",
        "cmap_diff" : "BrBG",
        "clevels_plain"       : np.linspace(0, 2, 51),
        "clevels_plain_tick"  : np.array([0, 0.5, 1, 1.5, 2,]) ,
        "clevels_diff" : np.linspace(-1, 1,  11),
        "factor"        : 1,
    },


}

"""
    "vice" : {
        "display"   : "Sea-ice volume [m^3 / m^2]",
        "cmap_mean" : "GnBu",
        "clevels_obs"  : np.linspace(0, 4, 11),
        "clevels_diff" : np.linspace(-1,   1, 11),
        "factor"       : 1.0,
    },


    "h_ML" : {
        "display"   : "Mixed-layer Thickness [m]",
        "cmap_mean" : "GnBu",
        "clevels_obs"  : np.linspace(0, 300, 31),
        "clevels_diff" : np.linspace(-100, 100, 21),
        "factor"        : 1.0,
    },


}
"""

boxes = [ 
    ["", [-15, 15], [50, 95], "r"],
    ["", [-15, 15], [150, 270], "r"],
    ["", [-15, 15], [320, 350], "r"],
]



proj1 = ccrs.PlateCarree(central_longitude=180.0)
data_proj = ccrs.PlateCarree(central_longitude=0.0)

proj_kw = {
    'projection':proj1,
    'aspect' : 'auto',
}


plot_vars = ["SST", "PREC_TOTAL"]
#plot_vars = ["TMXL", "XMXL"]
#plot_vars = ["SST", "PREC_TOTAL"]
#plot_vars = ["PREC_TOTAL",]

for m in [4,]:#[0,2,4,]:#range(5):

    rng=[
        [11, 0,  1],
        [ 2, 3,  4],
        [ 5, 6,  7],
        [ 8, 9, 10],
        slice(None),
    ][m]

    ext = [
        "DJF",
        "MAM",
        "JJA",
        "SON",
        "MEAN"
    ][m]

        
    print("Time : ", ext)
 
    # Original
    fig = plt.figure(constrained_layout=False, figsize=(5 * len(plot_vars), 3 * len(sim_casenames)))
    heights  = [1,] * len(sim_casenames) + [0.1]
    widths   = [1,] * len(plot_vars)

    spec = fig.add_gridspec(nrows=len(heights), ncols=len(widths), width_ratios=widths, height_ratios=heights, wspace=0.2, hspace=0.3, right=0.8) 


    for (i, varname) in enumerate(plot_vars):
        
        plot_info = plot_infos[varname]

        ax = []
       
        factor = plot_info["factor"]

        clevels_diff  = plot_info["clevels_diff"]

        if "clevels_diff_ticks" in plot_info: #.haskey("clevels_diff_ticks"):
            clevels_diff_ticks = plot_info["clevels_diff_ticks"]
        else:
            clevels_diff_ticks = plot_info["clevels_diff"]

        if "cmap_diff" in plot_info:
            cmap_diff = cm.get_cmap(plot_info["cmap_diff"])
        else:
            cmap_diff = cm.get_cmap("bwr")
 
        print("Plotting ", varname)

#        fig.suptitle("[%s] %s" % (ext, plot_info["display"]))

        idx = 0
        for exp_name, caseinfo in sim_casenames.items():

            label = exp_name
            lc = caseinfo["lc"]
            ls = caseinfo["ls"]
            row_idx = idx#caseinfo["col_idx"]

            _ax = fig.add_subplot(spec[row_idx, i], **proj_kw)

            ax.append(_ax)
            
            
            var_mean = "%s_MM" % varname
            var_std  = "%s_MASTD" % varname
 

            _EXP = np.mean(data["EXP"][exp_name][var_mean][rng, :, :], axis=(0,)) * factor
            _CTL = np.mean(data["CTL"][exp_name][var_mean][rng, :, :], axis=(0,)) * factor

            _STD_EXP = np.mean(data["EXP"][exp_name][var_std][rng, :, :], axis=(0,)) * factor
            _STD_CTL = np.mean(data["CTL"][exp_name][var_std][rng, :, :], axis=(0,)) * factor

            if varname == "SST":

                _EXP[extrop_mask_idx] = np.nan
                _CTL[extrop_mask_idx] = np.nan

                _EXP[lnd_mask_idx] = np.nan
                _CTL[lnd_mask_idx] = np.nan


            _diff = _EXP - _CTL
            
            if varname == "SST":
                _diff_mean = area_mean(_diff, area)
            else:
                _diff_mean = 0

            
            
            _diff -= _diff_mean

            mappable_diff = _ax.contourf(lon, lat, _diff,  clevels_diff,  cmap=cmap_diff, extend="both", transform=data_proj)
            _ax.coastlines()

            #cs = _ax.contourf(lon, lat, cut_t_score, [0.0, threshold, threshold+1], alpha=0, hatches=[None, None, '...', '...'], extend="both", transform=data_proj)
#            artists, labels = cs.legend_elements()
#            _ax.legend(artists, labels, handleheight=2)

            #_ax.set_title("%s diff ( $\\Delta_{\\mathrm{mean}} = %.2f $ )" % (label, _diff_mean, ))
            if idx == 0:
                _ax.set_title(plot_info["display"])

            if i==0:
                _ax.text(-0.15, 0.5, "%s" % (label, ), rotation=90, va="center", ha="center", transform=_ax.transAxes)



            for box_label, lat_rng, lon_rng, linecolor in boxes:
                _ax.add_patch(patches.Rectangle((lon_rng[0], lat_rng[0]), lon_rng[1] - lon_rng[0], lat_rng[1] - lat_rng[0], linewidth=1, edgecolor=linecolor, facecolor='none', transform=data_proj))
            
            idx += 1

        for _ax in ax:
            gl = _ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=1, color='gray', alpha=0.3, linestyle='-')
            
            gl.xlabels_top = False
            gl.ylabels_right = False
            gl.xlocator = mticker.FixedLocator([-180, -90, 0, 90, 180])
            gl.ylocator = mticker.FixedLocator([-30, -20, -10, 0, 10, 20, 30])
            gl.xformatter = LONGITUDE_FORMATTER
            gl.yformatter = LATITUDE_FORMATTER

            gl.xlabel_style = {'size': 8, 'color': 'black', 'ha':'center'}
            gl.ylabel_style = {'size': 8, 'color': 'black', 'ha':'right'}
            _ax.set_extent([0, 360, -30, 30], crs=ccrs.PlateCarree())
 


        cax = fig.add_subplot(spec[-1, i])
        cb_diff = fig.colorbar(mappable_diff,  cax=cax, ticks=clevels_diff_ticks, orientation="horizontal")
        cb_diff.set_label("%s %s" % (plot_info["display"], plot_info["unit"]))
            



fig.savefig("figures/diff_map_%s.png" % ("-".join(plot_vars)), dpi=600)
plt.show()
plt.close(fig)

