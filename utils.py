# Some utitilties to read/convert data for EUMETSAT satellite archive
# In the future all data readers will be moved here 
import numpy as np # Import the Numpy package

def brigthness_temp(var):
    """ Compute the brightness temperature given input data, which should be 
        relative to the infrared channels of SEVIRI. The channel number is read
        from the NETCDF variable name, so that the correct coefficients for the
        conversions are used. 
        
        TO-DO. Check before if the value is masked. This should be a problem if
        the domain extends somehwere outside the satellite POV."""
    
    channels={
        'ch4':{'nu_c':2569.094, 'A':0.9959, 'B':3.471},
        'ch5':{'nu_c':1598.566, 'A':0.9963, 'B':2.219},
        'ch6':{'nu_c':1362.142, 'A':0.9991, 'B':0.485},
        'ch7':{'nu_c':1149.083, 'A':0.9996, 'B':0.181},
        'ch8':{'nu_c':1034.345, 'A':0.9999, 'B':0.060},
        'ch9':{'nu_c':930.659 , 'A':0.9983, 'B':0.627},
        'ch10':{'nu_c':839.661, 'A':0.9988, 'B':0.627},
        'ch11':{'nu_c':752.381, 'A':0.9981, 'B':0.576}
             }
    
    # these are universal
    C1=1.19104E-5
    C2=1.43877
    
    nu_c=channels[var.name]['nu_c']
    A=channels[var.name]['A']
    B=channels[var.name]['B']
    
    temp_b=( (C2*nu_c)/(A*np.ma.log((C1*nu_c**3/var[:])+1)) ) - (B/A)
    
    temp_b=temp_b-273.15
    
    return(temp_b)