# Required libraries
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from mpl_toolkits.basemap import Basemap # Import the Basemap toolkit
import numpy as np # Import the Numpy package
from cpt_convert import loadCPT # Import the CPT convert function
from matplotlib.colors import LinearSegmentedColormap # Linear interpolation for color maps
from datetime import datetime
from glob import glob

# Converts the CPT file to be used in Python
cpt = loadCPT('IR4AVHRR6.cpt')
# Makes a linear interpolation with the CPT file
cpt_convert = LinearSegmentedColormap('cpt', cpt)

path = '/work/mh0731/m300382/sat/ophelia/'

for fname in glob(path+"*.nc"):
    print(fname)
    # Search for the Scan Start in the file name
    time = (fname[fname.find("MG_")+3:fname.find(".nc")])

    # Format the "Observation Start" string
    date = datetime.strptime(time,'%Y%m%d%H%M%S')
    # Open the file using the NetCDF4 library
    nc = Dataset(fname)

    # Extract the Brightness Temperature values from the NetCDF
    ir_10p8 = np.ma.masked_less(nc.variables['ch9'][:], 10)
    lons = np.array(nc.variables['lon'])
    lats = np.array(nc.variables['lat'])

    nu_c=930.659
    alpha=0.9983
    beta=0.627
    C1=1.19104E-5
    C2=1.43877
    temp_b=( (C2*nu_c) / (alpha*np.log((C1*nu_c**3/ir_10p8)+1)) )- ( beta/alpha )
    temp_b=temp_b-273.15

    bmap = Basemap(projection='cyl', llcrnrlon=lons[0,0], llcrnrlat=lats[0,0], urcrnrlon=lons[-1,-1], urcrnrlat=lats[-1,-1],  resolution='i')
    # bmap = Basemap(projection='cyl', llcrnrlon=-40, llcrnrlat=30, urcrnrlon=-30, urcrnrlat=40,  resolution='i')

    bmap.contourf(lons,lats,temp_b,np.arange(-90,30,0.5),cmap=cpt_convert)

    # Draw the coastlines, countries, parallels and meridians
    bmap.drawcoastlines(linewidth=0.5, linestyle='solid', color='white')
    bmap.drawcountries(linewidth=0.5, linestyle='solid', color='white')
    bmap.drawparallels(np.arange(-90.0, 90.0, 10.0), linewidth=0.1, color='white', labels=[True, False, False, True])
    bmap.drawmeridians(np.arange(0.0, 360.0, 10.0), linewidth=0.1, color='white', labels=[True, False, False, True])

    # Insert the legend
    bmap.colorbar(location='right', label='Brightness Temperature [K]')

    date_formatted = datetime.strftime(date,'%H:%MZ %a %d %b %Y')
    plt.title(date_formatted)
#     plt.show()
    plt.savefig('./%s.png' % datetime.strftime(date,'%Y%m%d%H%M%S'), bbox_inches='tight', dpi=150)
    plt.clf()

plt.close('all')

