# Installation

EpiCure is a napari plugin. 
Depending on your familiarity with python, you can install it in several ways:

* [In a new virtual environment (recommend)](#from-a-virtual-environment-recommended): Usually, each plugin is installed in its own python environment to avoid compatibility issues of its dependencies. Below, we detailled all the installation steps so that anybody could perform this installation.

* [In already installed Napari](#from-napari-interface): if you already have an environement with napari installed (ideally with python 3.9 or 3.10), and are not afraid of compatibility issues, you can directly use it and add EpiCure to it.

* [In a full graphical way](#with-graphical-interface): if you are unconfortable with the installation of a virtual environment, there is a possibility to do all the installation through graphical interfaces.  


## From Napari interface
EpiCure is a Napari plugin, in python. 
You can install it through an already installed Napari instance by going in Napari to `Plugins>Install/Uninstall`, search for `Epicure` and click `Install`.
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

### Step 4: Open napari and start using EpiCure
You can open napari by writing `napari` in the terminal. 
It is often slow to open the first time but that’s it. 

You can start EpiCure by going in `Plugins>EpiCure>Start Epicure` and follow the [Usage online documentation](./Start-epicure.md) to know how to use it.


## With graphical interface 

### Step 1: Napari installation through a graphical interface

Download the bundle version of napari 0.5.4:

* [Linux version](https://github.com/napari/napari/releases/download/v0.5.4/napari-0.5.4-Linux-x86_64.sh)
* [Windows x86](https://github.com/napari/napari/releases/download/v0.5.4/napari-0.5.4-Windows-x86_64.exe)

* [MacOS arm64 (apple chip, from M1 and after)](https://github.com/napari/napari/releases/download/v0.5.4/napari-0.5.4-macOS-arm64.pkg) :fontawesome-solid-triangle-exclamation:
* [MacOS x86 (Intel chip, before M1)](https://github.com/napari/napari/releases/download/v0.5.4/napari-0.5.4-macOS-x86_64.pkg):fontawesome-solid-triangle-exclamation:

!!! warning "napari bundle doesn't open on MacOS" 
	On MacOS, the bundle version 0.5.4 might not work (after installation, it doesn't open, see more in [imagesc forum](https://forum.image.sc/t/bundle-napari-0-5-4-on-macos-permission-denied/117259)). In this case, proceed to the "normal" installation, or install the [latest napari bundle](https://napari.org/stable/tutorials/fundamentals/installation_bundle_conda.html#macos-bundle) (without epyseg then). 

Double-click on the executable.
It will open an installer program, that you can simply follow step by step.
You can keep all the default options that are proposed by the installation program.
When the installation is finished (it takes some time), a shortcut icon should have been created in your desktop.

![snapshots installation](./imgs/bundle_installation.png)

All these bundles come from napari github, [release of version 0.5.4](https://github.com/napari/napari/releases/tag/v0.5.4). 
The installation steps for each OS are described [here](https://napari.org/stable/tutorials/fundamentals/installation_bundle_conda.html).

??? note "Why napari version 0.5.4" 
	We chose this version as it is the last one in Python 3.9, the following ones are with Python > 3.11, to have all options available (including Epyseg which is limited to version <3.11).
	You can still download the latest bundle of napari if you wish, and then use the napari console Terminal to fix dependencies install, or not use some options (Epyseg).

### Step 2: EpiCure installation through a graphical interface
When the installation is over, double-click on the napari icon and wait for napari window to open (it can take a few minutes). 
When napari is open, go to `Plugins>Install/Uninstall` to open the plugin manager.
In the window that appears, search for `epicure` and click Install.
Wait for the installation to finish (it takes some time), and restart napari.

![snapshots plugin installation](./imgs/bundle_plugin_install.png)

If you want to install a specific version of EpiCure, click on `Installation info` to get the list of available versions.
**Restart napari after the plugin installation**.

### Step 3: Use EpiCure from Napari
Open Napari by double-clicking on the icon created by the installation in step 1.

In the napari window, start EpiCure by going in `Plugins>EpiCure>Start Epicure` and follow the [Usage online documentation](./Start-epicure.md) to know how to use it.

??? tip "Updating some dependencies version"
	If you need to change some dependencies version, you can do so by opening the napari Terminal by clicking the icon :material-console-line: at the bottom left of the napari window. Then write `pip install modulename==versionnumber` to install the `modulename` library with the given version number.

