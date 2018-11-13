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

# Converts the CPT file to be used in Python
cpt = loadCPT('IR4AVHRR6.cpt')
# Makes a linear interpolation with the CPT file
cpt_convert = LinearSegmentedColormap('cpt', cpt)

folder = '/work/mh0731/m300382/sat/zorbas/'
first=True

for fname in glob(folder+"W_XX-EUMETSAT-Darmstadt,VIS+IR+IMAGERY,MSG3+SEVIRI_C_EUMG_20180928120009.nc"):
    # Search for the Scan Start in the file name
    time = (fname[fname.find("MG_")+3:fname.find(".nc")])
    # Format the "Observation Start" string
    date = datetime.strptime(time,'%Y%m%d%H%M%S')

    # Check if we already created the image
    image_string='./images/'+datetime.strftime(date,'%Y%m%d%H%M%S')+'.png'
    #if os.path.isfile(image_string):
    #    print('Skipping '+fname)
    #    continue

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

        # bmap = Basemap(projection='cyl', llcrnrlon=15, llcrnrlat=37,\
        # urcrnrlon=22, urcrnrlat=42,  resolution='i')
        # bmap = Basemap(projection='cyl', llcrnrlon=-50, llcrnrlat=20, urcrnrlon=-5, urcrnrlat=60,  resolution='l')
        # bmap = Basemap(projection='stere', llcrnrlon=lons[0,0], llcrnrlat=lats[0,0], urcrnrlon=lons[-1,-1], urcrnrlat=lats[-1,-1],\
        #                lon_0=0, lat_0=35,  resolution='l')
        bmap = Basemap(projection='stere', llcrnrlon=7, llcrnrlat=30, urcrnrlon=30, urcrnrlat=44,\
                       lon_0=15, lat_0=38,  resolution='i')
        # Draw the coastlines, countries, parallels and meridians
        first=False

    x,y=bmap(lons,lats)
    print(temp_b.min())
    print(temp_b.max())
    bmap.contourf(x,y,temp_b,np.arange(-60,40,0.1),cmap=cpt_convert,extend="both")
    #bmap.contourf(x,y,ir_10p8,np.arange(0,120,1),cmap="gist_gray_r",extend="both")
    bmap.drawcoastlines(linewidth=1, linestyle='solid', color='white')
    bmap.drawcountries(linewidth=1, linestyle='solid', color='white')
    bmap.drawparallels(np.arange(-90.0, 90.0, 10.), linewidth=0.5, color='white', labels=[False, False, False, False])
    bmap.drawmeridians(np.arange(0.0, 360.0, 10.), linewidth=0.5, color='white', labels=[False, False, False, False])

    # Insert the legend
    # bmap.colorbar(location='right', label='Brightness Temperature [K]')

    date_formatted = datetime.strftime(date,'%H:%MZ %a %d %b %Y')
    # plt.title(date_formatted+" | "+u"\N{COPYRIGHT SIGN}"+'EUMETSAT - prepared by Guido Cioni (www.guidocioni.it)',fontsize=10 )
    # plt.title(date_formatted+" | "+u"\N{COPYRIGHT SIGN}"+'EUMETSAT',fontsize=10 )

    # plt.show()
    plt.savefig('./images/%s.png' % datetime.strftime(date,'%Y%m%d%H%M%S'), bbox_inches='tight', dpi=150)
    plt.clf()

plt.close('all')
