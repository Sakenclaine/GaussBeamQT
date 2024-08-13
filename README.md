# GaussBeamQT
Small tool to visualise the beam profile following gaussian beam optics.

Most of the input values need to be applied by pressing enter. If the plot is not update although values changed, try pressing udate plot.

# Run/Build It Yourself
To run the program either download the executable (Windows only) or run the python code locally.
The executable is created using PyInstaller (https://pyinstaller.org) running 
```
pyinstaller --name "GaussBeamQT" --icon=GB_icon.png main.py
```
In order to run the source code create a python environment containing the packages given in the .yml file 
and the run main.py.  
