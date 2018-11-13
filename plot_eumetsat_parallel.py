# -*- coding: utf-8 -*-
# Required libraries
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


def main():
    folder = '/work/mh0731/m300382/sat/ilona/'
    fnames = chunks(glob(folder+"*.nc"), 10)
    p = Pool(8)
    p.map(plot_files, fnames)

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

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
        image_string='./images/'+datetime.strftime(date,'%Y%m%d%H%M%S')+'.png'
        if os.path.isfile(image_string):
            print('Skipping '+fname)
            continue

        print('Using '+fname)
        # Open the file using the NetCDF4 library
        nc = Dataset(fname)
        # Extract the Brightness Temperature values from the NetCDF
        ir_10p8 = np.ma.masked_less(nc.variables['ch9'][:], 10)

        nu_c=930.659
        alpha=0.9983
        beta=0.627
        C1=1.19104E-5
        C2=1.43877
        temp_b=( (C2*nu_c) / (alpha*np.ma.log((C1*nu_c**3/ir_10p8)+1)) )- ( beta/alpha )
        temp_b=temp_b-273.15

        if first:
            lons = np.ma.masked_less(np.array(nc.variables['lon']), -180)
            lats = np.ma.masked_less(np.array(nc.variables['lat']), -90)
            bmap = Basemap(projection='stere', llcrnrlon=-8, llcrnrlat=35, urcrnrlon=21, urcrnrlat=45,\
                       lon_0=10, lat_0=38,  resolution='i')
            # Draw the coastlines, countries, parallels and meridians
            first=False

        x,y=bmap(lons,lats)
        bmap.contourf(x,y,temp_b,np.arange(-80,30,0.1), cmap=cpt_convert, extend="both")
        bmap.drawcoastlines(linewidth=0.5, linestyle='solid', color='white')
        bmap.drawcountries(linewidth=0.5, linestyle='solid', color='white')
        bmap.drawparallels(np.arange(-90.0, 90.0, 5.), linewidth=0.2, color='white', labels=[True, False, False, True], fontsize=7)
        bmap.drawmeridians(np.arange(0.0, 360.0, 5.), linewidth=0.2, color='white', labels=[True, False, False, True], fontsize=7)

        # Insert the legend
        bmap.colorbar(location='right', label='Brightness Temperature [C]', fraction=0.046, pad=0.04)

        date_formatted = datetime.strftime(date,'%H:%MZ %a %d %b %Y')
        plt.title(date_formatted+" | "+u"\N{COPYRIGHT SIGN}"+'EUMETSAT - prepared by Guido Cioni (www.guidocioni.it)', fontsize=8)
        plt.savefig('./images/%s.png' % datetime.strftime(date,'%Y%m%d%H%M%S'), bbox_inches='tight', dpi=200)
        plt.clf()

    plt.close('all')


if __name__ == "__main__":
    main()
