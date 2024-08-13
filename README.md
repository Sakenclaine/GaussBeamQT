# GaussBeamQT
Small tool to visualise the beam profile following gaussian beam optics.
Most of the input values need to be applied by pressing enter. If the plot is not update although values changed, try pressing udate plot.
To view the beamradius at a position z in propagation direction drag the blue cursor line. The label showing the radius for x and y axis and the z-position can be moved vertically if obscured.

![grafik](https://github.com/user-attachments/assets/7a4d5256-4c1f-4b65-9b22-cd2c57f90a99)


# Run/Build It Yourself
To run the program either download the executable (Windows only) or run the python code locally.
The executable is created using PyInstaller (https://pyinstaller.org) running 
```
pyinstaller --name "GaussBeamQT" --icon=GB_icon.png main.py
```
In order to run the source code create a python environment containing the packages given in the .yml file 
and then run main.py.  
