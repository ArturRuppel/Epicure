# Installation

## From Napari interface
EpiCure is a Napari plugin, in python. 
You can install it either through an already installed Napari instance by going in Napari to `Plugins>Install/Uninstall`, search for `Epicure` and click `Install`.
You could have version issues between the different modules installed in your environment and EpiCure dependencies, in this case it is recommended to create a new virtual environnement specific for EpiCure.


## From a virtual environment (recommended)

To install EpiCure in a new environnement, you should create a new virtual environnement or activate an exisiting compatible one.

### Step 1 : install a Python management package (if you don't have one already). 
You have different options, but you have to choose one:  

- Miniforge (**recommended**): fast, free but no interface. Follow the detailled steps here to [install miniforge](https://kirenz.github.io/codelabs/codelabs/miniforge-setup/#0)
- venv: fast and simple install in general, no interface. See [tutorial here](https://www.geeksforgeeks.org/create-virtual-environment-using-venv-python/)
- Mamba: fast, free but no interface. See [here](https://informatics.fas.harvard.edu/resources/tutorials/installing-command-line-software-conda-mamba/)
- Anaconda: a sort of interface, works well on MacOS and Windows but slow and might not stay free to all. See here: [on windows](https://www.geeksforgeeks.org/how-to-install-anaconda-on-windows/), [on macOS](https://www.geeksforgeeks.org/installation-guide/how-to-install-anaconda-on-macos/?ref=ml_lbp) or [on linux](https://www.geeksforgeeks.org/how-to-install-anaconda-on-linux/) ). 
 
### Step 2 : Create a virtual environment with that python management package. 
Once you have installed such Python management package, they generally create one environment called `base` but you should not install anything in that environment.  

- You need to create an environment where you will install EpiCure. To do so you first open the terminal (activated in the `base` environment), and type: 
```
    conda create -n epicurenv python=3.10
``` 
It will install python 3.10 and create an environment called `epicurenv`. 


!!! warning "Python version"
    If you wish to use the option to segment the movie with Epyseg, you must use a python version until <= 3.10. Indeed, epyseg is not compatible on more recent versions. By default, we recommend 3.10 so that everything is compatible


### Step 3: Install EpiCure 
Once you have created/identified a virtual environnement, type in the terminal:
``` 
conda activate epicurenv
```
to activate it (and start working in that environnement).

Type in the activated environnement window:

```
pip install epicure 
```
to install EpiCure with its dependencies.

**Step 4: Open napari and start using EpiCure **
You can open napari by writing `napari` in the terminal. 
It is often slow to open the first time but that’s it. 

You can start EpiCure by going in `Plugins>EpiCure>Start Epicure` and follow the [Usage online documentation](./Start-epicure.md) to know how to use it.

## Compatibility/Dependencies
