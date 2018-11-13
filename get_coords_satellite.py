# Required libraries
from mpl_toolkits.basemap import Basemap # Import the Basemap toolkit
import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy as np # Import the Numpy package
from cpt_convert import loadCPT # Import the CPT convert function
from matplotlib.colors import LinearSegmentedColormap # Linear interpolation for color maps
from datetime import datetime
from glob import glob
import os
from utils import brigthness_temp

# Converts the CPT file to be used in Python
cpt = loadCPT('IR4AVHRR6.cpt')
# Makes a linear interpolation with the CPT file
cpt_convert = LinearSegmentedColormap('cpt', cpt)

path = '/work/mh0731/m300382/sat/ilona/'

fnames=sorted(glob(path+"*.nc"))
first=True
coords=[]
dates=[]

# for fname in fnames[35:340]:
for fname in fnames[35:340]:
    # Search for the Scan Start in the file name
    time = (fname[fname.find("MG_")+3:fname.find(".nc")])
    # Format the "Observation Start" string
    date = datetime.strptime(time,'%Y%m%d%H%M%S')

    image_string='./images/'+datetime.strftime(date,'%Y%m%d%H%M%S')+'.png'

    print('Using '+fname)
    # Open the file using the NetCDF4 library
    nc = Dataset(fname)
    # Extract the Brightness Temperature values from the NetCDF    
    temp_b = brigthness_temp(nc.variables['ch9'])
    
    if first:
        lons = np.ma.masked_less(nc.variables['lon'][:], -180)
        lats = np.ma.masked_less(nc.variables['lat'][:], -90)
        bmap = Basemap(projection='cyl', llcrnrlon=-8, llcrnrlat=35, urcrnrlon=21, urcrnrlat=45, resolution='i')
        # Draw the coastlines, countries, parallels and meridians
        x,y = bmap(lons,lats)
        first = False 
        
        def plot_figure():
                bmap.pcolormesh(x, y, temp_b, vmin=-80, vmax=30, cmap=cpt_convert)
                bmap.drawcoastlines(linewidth=0.5, linestyle='solid', color='white')
                bmap.drawcountries(linewidth=0.5, linestyle='solid', color='white')
                bmap.drawparallels(np.arange(-90.0, 90.0, 5.), linewidth=0.2, color='white',
                       labels=[True, False, False, True], fontsize=7)
                bmap.drawmeridians(np.arange(0.0, 360.0, 5.), linewidth=0.2, color='white',
                       labels=[True, False, False, True], fontsize=7)
                # Insert the legend
                bmap.colorbar(location='right', label='Brightness Temperature [C]', fraction=0.046, pad=0.04)
                date_formatted = datetime.strftime(date,'%H:%MZ %a %d %b %Y')
                plt.title(date_formatted+" | "+u"\N{COPYRIGHT SIGN}"+'EUMETSAT - prepared by Guido Cioni (www.guidocioni.it)',
                      fontsize=8)

    # Get coordinates on click
    def onclick(event):
        global ix, iy
        ix, iy = event.xdata, event.ydata
        coords.append((ix, iy))
        dates.append(datetime.strftime(date,'%Y%m%d%H%M%S'))
        print("clicked (%5.3f,%5.3f)"%(ix, iy))

    plt.ion()
    fig = plt.figure(figsize=(15, 15))
    plot_figure()
    fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show(block=True)

np.savetxt('coords.txt', np.array(coords), fmt='%5.3f %5.3f', header='longitude latitude')
np.savetxt('dates.txt', np.array(dates), fmt='%s', header='dates')