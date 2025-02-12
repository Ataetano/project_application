import numpy as np

def le(t, xyz, *args, **kwargs):
        """
        ********************************************************************************
        "I didn't have any knowledge about Chaotic System" you say,
        Nah Just use this one and change to any chaotic system you want later.
        Chaotic Trajectory parameter:
        d: 10 
        r: 28 
        b: 8/3 
        ********************************************************************************
        !!! This function relate with rk4 !!!
        """
        d, r, b = kwargs['d'], kwargs['r'], kwargs['b']
        x = xyz[0]
        y = xyz[1]
        z = xyz[2]
        xdot = d*(y - x)
        ydot = x*(r - z) - y
        zdot = x*y - b*z
        return np.array([xdot, ydot, zdot])