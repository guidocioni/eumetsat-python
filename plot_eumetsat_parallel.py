# -*- coding: utf-8 -*-
# Required libraries
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# %matplotlib
from netCDF4 import Dataset
from mpl_toolkits.basemap import Basemap # Import the Basemap toolkit
import numpy as np # Import the Numpy package
from cpt_convert import loadCPT # Import the CPT convert function
from matplotlib.colors import LinearSegmentedColormap # Linear interpolation for color maps
from datetime import datetime
from glob import glob
import os
from multiprocessing import Pool
from utils import *

folder = '/Users/thd5tt/Downloads/sat/'
channel = 'ch9'
channel_hrv = 'ch12'

def main():
    fnames = chunks(glob(folder+"*20200916*.nc"), 10)
    p = Pool(8)
    p.map(plot_files, fnames)

def plot_files(fnames):
    # Converts the CPT file to be used in Python
    cpt = loadCPT('IR4AVHRR6.cpt')
    # Makes a linear interpolation with the CPT file
    cpt_convert = LinearSegmentedColormap('cpt', cpt)

    first=True

    for fname in fnames:
        # Search for the Scan Start in the file name
        time = (fname[fname.find("MG_")+3:fname.find(".nc")])
        # Format the "Observation Start" string
        date = datetime.strptime(time,'%Y%m%d%H%M%S')

        # Check if we already created the image
        image_string = folder+'images/%s_%s.png' % (channel, datetime.strftime(date,'%Y%m%d%H%M%S'))
        if os.path.isfile(image_string):
            #print('Skipping '+fname)
            continue

        print('Using '+fname)
        # Open the file using the NetCDF4 library
        nc = Dataset(fname)
        # Extract the Brightness Temperature values from the NetCDF
        temp_b = brigthness_temp(nc.variables[channel])
        hrv =  nc.variables[channel_hrv][:]

        fig = plt.figure(figsize=(15, 15))

        if first:
            lons = np.ma.masked_less(np.array(nc.variables['lon']), -180)
            lats = np.ma.masked_less(np.array(nc.variables['lat']), -90)

            lats_hrv, lons_hrv = create_coord_hrv(lats, lons)
            
            bmap = Basemap(projection='cyl', llcrnrlon=4, llcrnrlat=31, 
                            urcrnrlon=26, urcrnrlat=45, resolution='i')
            
            x, y = bmap(lons, lats)
            x_hrv, y_hrv = bmap(lons_hrv, lats_hrv)
            
            first = False

        if (hrv.std() > 0.9):
            bmap.pcolormesh(x_hrv, y_hrv, hrv, vmin=0, vmax=20, cmap='gray')
            bmap.pcolormesh(x, y, np.ma.masked_array(temp_b, temp_b > -38),
                            vmin=-80, vmax=50, cmap=cpt_convert,
                            alpha=0.3, linewidth=0, antialiased=True)
        else:
            bmap.pcolormesh(x, y, temp_b, vmin=-80, vmax=50, cmap=cpt_convert,
                antialiased=True)

        bmap.drawcoastlines(linewidth=0.5, linestyle='solid', color='white')
        bmap.drawcountries(linewidth=0.5, linestyle='solid', color='white')
        bmap.drawparallels(np.arange(-90.0, 90.0, 5.), linewidth=0.2,
                 color='white', labels=[True, False, False, True], fontsize=7)
        bmap.drawmeridians(np.arange(0.0, 360.0, 5.), linewidth=0.2, 
                color='white', labels=[True, False, False, True], fontsize=7)

        # Insert the legend
        bmap.colorbar(location='right', label='Brightness Temperature [C] / HRV radiance',
                         size='2%', pad='1%')

        date_formatted = datetime.strftime(date,'%a %d %b %Y, %H:%MZ')
        annotation(plt.gca(), date_formatted,
                        loc='upper center',fontsize=9)
        annotation(plt.gca(), "SEVIRI %s,%s High Rate data" %(channel, channel_hrv) + u"\N{COPYRIGHT SIGN}"+'EUMETSAT - prepared by Guido Cioni (www.guidocioni.it)' ,
                        loc='lower left', fontsize=7)
        #print('Saving file %s' % image_string)
        plt.savefig(image_string, bbox_inches='tight', dpi=200)
        plt.clf()

    plt.close('all')


if __name__ == "__main__":
    main()
