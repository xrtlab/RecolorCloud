# RecolorCloud - A complementary tool for labelCloud 

This is a tool that is meant to be used alongside tools that can provide the ability to convert a point cloud into a recolored point cloud based on the bounding boundaries created by labelCloud. Currently the way it functions is based sorely on volumetric cropping of a starting pointcloud. The end output is a point cloud file type which can be supporteed by the editing engine; Open3D. 

<p align="Center">
    <img src="https://github.com/xrtlab/RecolorCloud/blob/ac7d343452a364731b757f0c1b55a8722b6739fa/Images/RecolorCloud%20Reworked.PNG"/>
</p>


## Features

This progam currently has the following features:

- Recoloring a point cloud given a color look-up table and a labelCloud bounding box file
- Segmenting a point cloud given a labelCloud bounding box file
- Recoloring a point cloud given a labelCloud bounding box file and two colors to recolor from
- Downsample the point cloud
- Conver the point cloud into different formats

## Supported file types for point clouds

This program can support multiple file types as ran by Open3D. These include: 
- .las
- .laz
- .ply
- .pts
- .pcd
- .xyz
- .xyzn
- .xyzrgb

Current file support is detailed in this [link](http://www.open3d.org/docs/release/tutorial/geometry/file_io.html?highlight=pts).


## Dependencies

``` bash
Phython 3.10.- or greater
Open3D  0.18.1
Scipy 1.5.2
Numpy 1.19.2

```

A **requirements.txt** is provided so you can install the dependencies to RecolorCloud without guessing them. A virtual python environment is highly encouraged but not necessary and if using one, it is highly encouraged but optional to use Anaconda to create a virtual environment for installing and handling the dependencies. 

## How to use?

Dependening on how you have set up your environment, either start a virtual environment with python dependencies. Next proceed to run the codebase by running: 

``` bash
cd \RecolorCloud
python .\main
```

As of the current version, this is the only way to run the program.

Upon starting the program, you will be met with the present interface. The necessary files are detailed in the program but essentially you will always require 3 files. These are:

- A point cloud (Supported file types are detailed in "Supported file types")
- A JSON generated from labelCloud using a centroid_rel export style
- A TXT file created and formatted as seen in `input/rgb_labeling` 

### LabelCloud File

This file is simply a JSON file organized to be relative to a position defined by labelCloud. By default this means labelCloud puts the bounding boxes relative to the max and min of a pointCloud divided by the total point count for each of the XYZ axis. 

### TXT File

This simply acts as a look-up table for which colors are drawn from in a formatted style. The current style is: 

`label r g b enabled-flag`

The enabled flag allows the user to set a specified label to effect the point cloud. The flag has different effects depending on the editing mode selected. These options are detailed below:

#### Recoloring a point cloud 
If the flag is enabled, the bounding box will be exported in the final point cloud, otherwise it will be ignored. 

#### Segmenting a point cloud
This works the same as in recoloring a point cloud.

#### Recoloring by range 

By selecting one of the options in the menu for recoloring the point cloud, the user can recolor a section of the point cloud with given colors. This works through linear interpolation of the colors of gradient between two or more selected colors. The reference to how this works is given on this [website](https://bsouthga.dev/posts/color-gradients-with-python).

Two modes are currently implemented using linear interpolation, the first one is done by giving two colors as the start and end points. The second method uses a given set of RGB or HEX values to determine colors. An example file is given at /input/Example RGB Palette. 

Users input a value in the entry field with either RGB values separated with a space or Hex values. 
Ex.: 
0,0,0 1,1,1 2,2,2 ... 
#000000 #FFFFFF ...

I was considering implementing bezier curve calculations but this is not a priority at the moment. 

Once a selected set of colors has been created. RecolorCloud will recolor items with a 1 flag from the RGB Labels file. Items currently are recolored by randomly selecting a color from the pool of colors interpolated from given RGB values. 

### Notes on functionality

Please note that this is still a work in progress. There are multiple bugs that I'm still working out as well as features that are coming but not yet implemented. I will try working these out towards a 1.0v version. 

## Notes on funding and other notes. 

This tool is not directly funded by a grant, however it is being created in direct interest to one being worked in at UCF for the NSF under the project name of InfraStructure for Photorealistic Image and Environment Synthesis (I-SPIES).

## License

This work is currently being worked as an MIT versioned software. 

## Credits

Currently the lead author on this project; Esteban Segarra M. 
