#Author: Esteban Segarra 
#Purpose: To run a set of tools used to be applied on a point cloud that would be modified for a set of cases such as: 
#           - Segmenting the dataset
#           - Recoloring certain sections
#           - Separating the point cloud using different sections
# This tool was develoepd using the intent the user has defined points of interest using LabelCloud. Users can find more information on what specific
# data is being used for segmenting the point cloud in labelCloud. 
#
# This tool is developed as part of the UCF XRT Lab 
# Users are encouraged to leave issues at the github repo.


### Imports
from email.mime import application
from fileinput import filename
import numpy
from pointcloudTool import PCTools_Utils
import open3d
import os
import webbrowser
from PyQt5.QtWidgets import (QAction, QApplication, QFormLayout, QGroupBox,
                             QLabel, QPushButton, QVBoxLayout, QWidget,
                             QMainWindow, QLineEdit, QInputDialog, QFileDialog, QMessageBox,
                             QRadioButton, QColorDialog,QCheckBox, QSizePolicy)
from PyQt5.QtCore import Qt,pyqtSlot
from PyQt5.QtGui import QPixmap, QColor,QIcon, QPainter, QPen,QIcon,QFont
import re


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.pointcloud_extensions = ["*.pts","*.ply","*.pcd"]
        
        self.addMenu()
        # self.createActions()
        
        #Application variables for the program in point cloud recoloring
        self.pointcloud_file_path = ""
        self.labelCloud_file_path = ""
        self.RGB_labels_file_path = ""
        self.output_file_path     = ""
        
        
        self.label_button_text_PC = QLineEdit()
        self.label_button_text_LC  = QLineEdit()
        self.label_button_text_RGB = QLineEdit()
        self.label_field_file_name = QLineEdit()
        
        
        self.label_status_PC = QLabel("Nothing Loaded")
        self.label_status_LC = QLabel("Nothing Loaded")
        self.label_status_RGB = QLabel("Nothing Loaded")     
        self.label_status_out = QLabel("No user-defined location")     
        
        self.activateRangedRecoloring = False

        #Utility variables for the program 
        self.localDir = os.getcwd()
        
        #Input directories
        self.inPointCloudDir = "input\\pointclouds"
        self.inLabelCloudDir = "input\\labelCloud_dat"
        self.inRgbDataDir    = "input\\rgb_labeling"
        
        
        
        self.accessedPC = False
        self.accessedLC = False
        self.accessedRGB = False
        
        self.log = ['','','','','']
        
        #Output directories
        self.outRange     = "output\\range_recolored"
        self.outRecolor   = "output\\recolored_by_label"
        self.outSegmented = "output\\segmented_by_label"
        
        #Quickly Recolor the labels to match status of program
        self.recolor_QLabel(self.label_status_PC, QColor(0,0,153),255)
        self.recolor_QLabel(self.label_status_LC, QColor(0,0,153),255)
        self.recolor_QLabel(self.label_status_RGB, QColor(0,0,153),255)
        self.recolor_QLabel(self.label_status_out, QColor(0,0,153),255)

        self.radioRecolorBut = QCheckBox("Range Recolor")
        
        #Storing utility classes 
        self.PCUtilTools = PCTools_Utils() #PC Tools Class
        
        #Make the UI Happen
        self.createUI()
    
    #This adds a taskbar to the top of the program.
    def addMenu(self):
        menuBar = self.menuBar()
        # fileMenu = menuBar.addMenu("File")
        helpMenu = menuBar.addMenu("Visit us on Github")
        
        # Create actions

        visitWebsiteAction = QAction('Visit Our Website', self) #.triggered.connect(self.wrapperOpenWebsite)
        fileBugReportAction = QAction('File a Bug Report', self)#.triggered.connect(self.wrapperOpenIssuesPage)

        # Add dropdown menu items on the Help menu

        helpMenu.addAction(visitWebsiteAction)
        helpMenu.addAction(fileBugReportAction)
        
        visitWebsiteAction.triggered.connect(self.wrapperOpenWebsite)
        fileBugReportAction.triggered.connect(self.wrapperOpenIssuesPage)
 
    #For sanity, these fuctions are for recoloring the background of some respective components.
    def recolor_QLabel(self, component, color= QColor(0,0,0),alpha = 255):
        component.setAutoFillBackground(True) # This is important!!
        values = "{r}, {g}, {b}, {a}".format(r = color.red(),
                                            g = color.green(),
                                            b = color.blue(),
                                            a = alpha
                                            )
        component.setStyleSheet("QLabel { color: rgba(" + values + "); }")
        
    #This one recolors the background of the said button. 
    def recolor_QPushButton(self, component, color= QColor(0,0,0),alpha = 255):
        component.setAutoFillBackground(True) # This is important!!
        values = "{r}, {g}, {b}, {a}".format(r = color.red(),
                                            g = color.green(),
                                            b = color.blue(),
                                            a = alpha
                                            )
        component.setStyleSheet("QPushButton { background-color: rgba(" + values + "); }")
        
    def createUI(self):
        # Create window
        self.setWindowTitle("RecolorCloud")
        self.setWindowIcon(QIcon('Program_Icon.png'))
        self.setGeometry(50, 50, 300, 1000)
        # self.setMinimumSize(500, 450)
        
        # Create central widget and layout
        self._centralWidget = QWidget()
        self._verticalLayout = QVBoxLayout()
        self._centralWidget.setLayout(self._verticalLayout)
        # Set central widget
        self.setCentralWidget(self._centralWidget)
        
        # Vertically center widgets
        self._verticalLayout.addStretch(1)

        # self.addHelpBox()

        self.addBrowseForFile("Step 1: Load Point Cloud (See dropdown in file selection for formats)\n",
                              "Browse for point cloud file", 
                              self.pointcloud_file_path
                              , ".pts", 0)
        self.addBrowseForFile("Step 2: Load labelCloud File (.json)\n",
                              "Browse for labelCloud file" ,
                              self.labelCloud_file_path
                              , ".json", 0)
        self.addBrowseForFile("Step 3: Load RGB Lables for Classes (.txt)\n",
                              "Browse for label-to-color file",
                              self.RGB_labels_file_path
                              , ".txt", 0)
        
        #Add the Recolor Section
        self.addRadioButtonSelection()
        self.addBrowseForFile("File output location (.laz,.las,.xyz,.xyzrgb,.xyzn,.pts,.ply, or .pcd)\n",
                              "Browse...",
                              self.output_file_path,
                              ".out",0)
        self.addFinalButtonSelections()
        
        self.addLogger()
         
         
        # Vertically center widgets
        self._verticalLayout.addStretch(1)
   
    def addHelpBox(self):
       #This is the button and file path shower. 
        groupBox = QGroupBox()
        groupBox.setFixedWidth(350)
        formLayout = QFormLayout()
        
        #Buttons for selecting start and end of the range of colors.
        helpBox =  QLabel("To begin progam operations, load files from steps 1-3.\nNext, choose which operation to perform on the point cloud by pressing the respective button.\n")
        helpBox.setWordWrap(True)
        
        formLayout.addRow(helpBox)

        groupBox.setLayout(formLayout)
        self._verticalLayout.addWidget(groupBox, alignment=Qt.AlignCenter)
   
    #These are the core wrappers for functionality. 
    def wrapperCreatePCFromLC(self):
        self.loggingWrapper("Creating semantic point cloud...")
        self.PCUtilTools.recolor_point_cloud()
        self.loggingWrapper("Done creating semantic point cloud.")
        self.exportPCRecolor.setEnabled(True)
    
    def wrapperSegmentPCFromLC(self):
        self.loggingWrapper("Segmenting Point Cloud...")
        self.PCUtilTools.segment_point_cloud()
        self.loggingWrapper("Done segmenting point cloud.")
        # self.segmentPCwithLC.setEnabled(True)
        self.exportPCSegmentation.setEnabled(True)
    
    
    def wrapperDownsamplePC(self):
        self.loggingWrapper("Downsampling Point Cloud...")
        try:   
            self.PCUtilTools.downsample_point_cloud(int(self.label_field_downscaling_option.text()),float(self.label_field_downscaling_scale.text()))
            self.loggingWrapper("Done downsampling point cloud.")
        except:
            self.loggingWrapper("ERROR: Please use a valid downsample value (0.0 - 1.0)")
        self.exportPCAny.setEnabled(True)
    
    
    def wrapperRecolorPC(self):
        self.PCUtilTools.toggle_threshold_recoloring(self.checkbox_change_mode.isChecked())
                
        self.PCUtilTools.set_coloring_mode(self.colorMode)
        self.PCUtilTools.toggle_gray_deletion(self.checkbox_grey_removal.isChecked())
        if (self.label_field_file_name.text() == "No file name."):
            self.loggingWrapper("No pointcloud file loaded.")
            return
        self.loggingWrapper("Recoloring Point Cloud...")
        
        if(not self.intervalsEntry.text().isdigit()):
            self.loggingWrapper("Interval is not a number. Using default values.")
        else:
            self.PCUtilTools.set_interval(int(self.intervalsEntry.text()))    
            
            
        #Going to be disabled for now. 
        if (self.colorMode == "bezier"):
            text = self.colorEntry.text()
            if (text == "Use this line for RGB/HEX colors used in replacement."):
                text = ""
            else:
                text_blocks = text.split(" ")
                if self.check_if_hex(text_blocks):
                    self.PCUtilTools.set_list_hex_colors(text_blocks)
                else:
                    self.PCUtilTools.set_list_rgb_colors(text_blocks)            

        # try: 
        if (not self.checkbox_change_mode.isChecked()):
            self.PCUtilTools.get_vectors_bbox()
        self.PCUtilTools.range_recolor_point_cloud()
        self.loggingWrapper("Done recoloring with range recoloring the point cloud.")
        self.exportRERange.setEnabled(True)
        # except:     
        #     self.PCUtilTools.call_3DViewer()
        
        # self.PCUtilTools.range_recolor_point_cloud()       
        # self.loggingWrapper("Done recoloring with range recoloring the point cloud.")
        # self.exportRERange.setEnabled(True)
 
    def check_if_hex(self,text_blocks):
        hex_mode = False
        #Each block is a color.
        for block in text_blocks:
                if ("#" in block and len(block) != 7):
                    self.loggingWrapper("Invalid hex color entry. Please check colors.")
                    return
                elif("#" in block and len(block) == 7):
                    hex_mode = True
                else:
                    hex_mode = False
        return hex_mode
        
    def wrapperExportPc(self):
        self.loggingWrapper("Exporting point cloud...")
        self.recolor_QPushButton( self.exportPCRecolor, color =QColor(255,255,0))
        
        
        # path = os.path.join(self.localDir, self.outRecolor)
        # os.chdir(path)
        name, extension = self.checkFieldPathForName(self.label_field_file_name,self.outRecolor)
        self.PCUtilTools.export_point_cloud(name)
        self.loggingWrapper("Done exporting point cloud.")
        self.recolor_QPushButton( self.exportPCRecolor, color =QColor(0,255,0))     

    def wrapperExportAsIs(self):
        self.loggingWrapper("Exporting point clouds...")
        self.recolor_QPushButton( self.exportPCConversion, color =QColor(255,255,0))
        
        # path = os.path.join(self.localDir, self.outRecolor)
        # os.chdir(path)
        name, extension = self.checkFieldPathForName(self.label_field_file_name,self.outRecolor)
        self.PCUtilTools.export_conversion_pc(name)
        self.loggingWrapper("Done exporting point cloud.")
        self.recolor_QPushButton( self.exportPCConversion,color =QColor(0,255,0))
        
        
    def wrapperExportLC(self):
        self.loggingWrapper("Exporting point clouds...")
        self.recolor_QPushButton( self.exportPCSegmentation, color =QColor(255,255,0))

        # path = os.path.join(self.localDir, self.outSegmented)
        # os.chdir(path)
        # filename = self.label_field_file_name.text()
        # filename = filename.split(".")
        # name = filename[0]
        # extension_file = filename[1]
        name, extension = self.checkFieldPathForName(self.label_field_file_name,self.outSegmented)
        self.PCUtilTools.export_point_clouds(name,"."+extension)
        self.loggingWrapper("Done exporting point cloud.")
        self.recolor_QPushButton( self.exportPCSegmentation,color =QColor(0,255,0))
        
        
    def wrapperExportRGB(self):
        self.loggingWrapper("Exporting point cloud...")
        self.recolor_QPushButton( self.exportRERange, color =QColor(255,255,0))
        
        
        # path = os.path.join(self.localDir, self.outRange)        
        # os.chdir(path)
        name, extension = self.checkFieldPathForName(self.label_field_file_name,self.outRange)
        self.PCUtilTools.export_point_cloud(name)
        self.loggingWrapper("Done exporting point cloud.")
        self.recolor_QPushButton( self.exportRERange, color =QColor(0,255,0))
 
 
    # Chuck in a QEditField here and get out a name and/or extension 
    def checkFieldPathForName(self,label_field, local_directory_location):
        textOut = label_field.text()
        if(":" in textOut or "/" in textOut):
            
            line = textOut.split("/")
            name = line[len(line)-1]
            extension = name.split(".")[1]
            
            textOut = textOut.replace(name, "")
            os.chdir(textOut)
            return name, extension
        else:
            path = os.path.join(self.localDir, local_directory_location)     
            os.chdir(path)
            filename = textOut.split(".")
            name = filename[0]
            extension_file = filename[1]
            return name, extension_file
        
    
 
    def wrapperOpenWebsite(self):
        webbrowser.open("https://github.com/xrtlab/RecolorCloud")
        
    def wrapperOpenIssuesPage(self):
        webbrowser.open("https://github.com/xrtlab/RecolorCloud/issues")

    ################################################
   
    def addFinalButtonSelections(self):
        #This is the button and file path shower. 
        groupBox = QGroupBox()
        groupBox.setFixedWidth(350)
        formLayout = QFormLayout()

        #Buttons for selecting start and end of the range of colors.
        # finalSelection =  QLabel("Filename: ")
        # finalSelection.setAlignment(Qt.AlignCenter)

        # self.label_field_file_name = QLineEdit("No file name.")
        # self.label_field_file_name.setAlignment(Qt.AlignCenter)


        # self.createRecoloredPCwithLC = QPushButton('Create point cloud recolored with Labels', self)
        self.createRecoloredPCwithLC = QPushButton('Semantically Recolor Point Cloud', self)
        self.createRecoloredPCwithLC.setToolTip('This creates a single point cloud recolored with labels from RGB and labelCloud boxes') 
        self.createRecoloredPCwithLC.clicked.connect(self.wrapperCreatePCFromLC)
        self.createRecoloredPCwithLC.setEnabled(False)

        self.exportPCRecolor = QPushButton('Export point cloud', self)
        self.exportPCRecolor.setToolTip('This exports the point cloud to a .pts file')
        self.exportPCRecolor.clicked.connect(self.wrapperExportPc)
        self.exportPCRecolor.setEnabled(False)

        self.segmentPCwithLC = QPushButton('Fragment the Point Cloud', self)
        self.segmentPCwithLC.setToolTip(' Warning: Make sure you have all selections from labelCloud! You are creating multiple point clouds!')
        self.segmentPCwithLC.clicked.connect(self.wrapperSegmentPCFromLC)
        self.segmentPCwithLC.setEnabled(False)

        self.exportPCSegmentation = QPushButton('Export point clouds', self)
        self.exportPCSegmentation.setToolTip('This exports the points cloud to .pts files')
        self.exportPCSegmentation.clicked.connect(self.wrapperExportLC)
        self.exportPCSegmentation.setEnabled(False)

        self.exportPCConversion = QPushButton('Instantly convert point cloud', self)
        self.exportPCConversion.setToolTip('Instantly converts and exports the point cloud.')
        self.exportPCConversion.clicked.connect(self.wrapperExportAsIs)
        self.exportPCConversion.setEnabled(False)

        # self.recolorWithRange = QPushButton('Recolor a selected region with ranged colors', self)
        self.recolorWithRange = QPushButton('Edit Point Cloud (Deleting or Recoloring)', self)
        self.recolorWithRange.setToolTip('Make sure you labled the regions of interest with desired colors!')
        self.recolorWithRange.clicked.connect(self.wrapperRecolorPC)
        self.recolorWithRange.setEnabled(False)
        
        self.exportRERange = QPushButton('Export point cloud', self)
        self.exportRERange.setToolTip('This exports the points cloud to a .pts file')
        self.exportRERange.clicked.connect(self.wrapperExportRGB)
        self.exportRERange.setEnabled(False)
        
        downsamplingLabel =  QLabel("Option 0: Voxel Downsampling \n  Option 1: Uniform Downsampling \n Option 2: Farthest Point Downsampling \n Option 3: Random Downsampling \n | Downsampling Factor |                         | Downsampling Method|")
        # finalSelection.setFont(QFont("Arial", 12, QFont.Bold))
        downsamplingLabel.setAlignment(Qt.AlignCenter)
        
        self.label_field_downscaling_scale = QLineEdit("Input % (0.0 - 1.0)")
        self.label_field_downscaling_scale.setAlignment(Qt.AlignCenter)
        
        self.label_field_downscaling_option = QLineEdit("1")
        self.label_field_downscaling_option.setAlignment(Qt.AlignCenter)
        
        self.downsamplePC = QPushButton('Downsample point cloud', self)
        self.downsamplePC.setToolTip('This downsamples the point cloud.')
        self.downsamplePC.clicked.connect(self.wrapperDownsamplePC)
        self.downsamplePC.setEnabled(True)
        
        #End formatting of the layout
        # formLayout.addWidget(self.createRecoloredPCwithLC,0,0)        
        
        # formLayout.addRow(finalSelection)
        # formLayout.addRow(self.label_field_file_name)
        self.exportPCAny = QPushButton('Export point cloud', self)
        self.exportPCAny.setToolTip('This exports the point cloud to a .pts file')
        self.exportPCAny.clicked.connect(self.wrapperExportPc)
        self.exportPCAny.setEnabled(False)
        
        
        formLayout.addRow(self.createRecoloredPCwithLC,self.exportPCRecolor)
        formLayout.addRow(self.segmentPCwithLC,self.exportPCSegmentation)
        formLayout.addRow(self.recolorWithRange,self.exportRERange)
        formLayout.addRow(downsamplingLabel)
        # formLayout.addRow(self.exportPCConversion,self.exportPCConversion)
        formLayout.addRow(self.label_field_downscaling_scale,self.label_field_downscaling_option)
        formLayout.addRow(self.downsamplePC)
        formLayout.addRow(self.exportPCConversion,self.exportPCAny)

        groupBox.setLayout(formLayout)
        self._verticalLayout.addWidget(groupBox, alignment=Qt.AlignCenter)

    #Just a random idea to slap at the bottom to show recent commands and status
    def addLogger(self): 
        #This is the button and file path shower. 
        groupBox = QGroupBox()
        groupBox.setFixedWidth(350)
        formLayout = QFormLayout()


        #Buttons for selecting start and end of the range of colors.
        logTitle = QLabel("]=================[Log]=================[\n")
        logTitle.setAlignment(Qt.AlignCenter)
        self.logBox1  = QLabel(" ")
        self.logBox2  = QLabel(" ")
        self.logBox3  = QLabel(" ")
        self.logBox4  = QLabel(" ")
        self.logBox5  = QLabel(" ")
        labelTemp = QLabel()
        labelCredit = QLabel("Tool powered by Open3D and the team at XRT Labs UCF")
        labelCredit.setAlignment(Qt.AlignCenter)
        
        pic = QPixmap('XRT_Logo_small.png')
        pic.scaledToWidth(50, Qt.SmoothTransformation)
        labelTemp.setPixmap(pic)
        labelTemp.setAlignment(Qt.AlignCenter)
        labelTemp.setWordWrap(True)
        
        labelEndLogging = QLabel("]=================[End Log]=================[\n")
        labelEndLogging.setAlignment(Qt.AlignCenter)
        
        formLayout.addRow(logTitle)
        # formLayout.addRow(self.logBox1)
        # formLayout.addRow(self.logBox2)
        formLayout.addRow(self.logBox3)
        formLayout.addRow(self.logBox4)
        formLayout.addRow(self.logBox5)
        # formLayout.addRow(labelEndLogging)
        # formLayout.addRow(labelCredit)
        formLayout.addRow(labelTemp)
        
        
        groupBox.setLayout(formLayout)
        self._verticalLayout.addWidget(groupBox, alignment=Qt.AlignCenter)
 
    #Incorporate this alongside the title bar. 
    def addActionsTitleBar(self):
        
        pass
   
    #Small wrapper for the logger. 
    def loggingWrapper(self, stringIn):
        self.log.append(stringIn)
        
        endIndex = len(self.log) - 1 
        self.logBox1.setText(self.log[endIndex - 4])
        self.logBox2.setText(self.log[endIndex - 3])
        self.logBox3.setText(self.log[endIndex - 2])
        self.logBox4.setText(self.log[endIndex - 1])
        self.logBox5.setText(self.log[endIndex])
        
        #Print out the log to the console.
        print(stringIn)
        
    #Need a couple of variables for making this part generic. 
    # Maybe, Title of Step, variable for file path, extension of file, status of button call 
    def addBrowseForFile(self, title="", button_title="", file_path="", extension="", status=0):
        #Setup the title of the dialog
        messageLabel = QLabel(title)
        messageLabel.setAlignment(Qt.AlignCenter)
        messageLabel.setWordWrap(True)
 
        #This is the button and file path shower. 
        groupBox = QGroupBox()
        groupBox.setFixedWidth(350)
        formLayout = QFormLayout()
        fileLabel = QLabel('File Path')
        
        # File field for the file path
        if extension == ".pts":
            fileField = self.label_button_text_PC  
        elif extension == ".json":
            fileField = self.label_button_text_LC   
        elif extension == ".out":
            fileField = self.label_field_file_name
        else:
            fileField = self.label_button_text_RGB  
            
        # fileField = QLineEdit()
        # fileField = labelFieldIn
        fileField.setTextMargins(3, 0, 3, 0)
        fileField.setMinimumWidth(200)
        fileField.setMaximumWidth(300)
        fileField.setClearButtonEnabled(True)

        #Button for calling the file browser dialog
        submitField = QPushButton(button_title)
        submitField.setCheckable(True)
        if extension == ".pts":
            submitField.clicked.connect(self.openFileNameDialogPC)
        elif extension == ".json":
            submitField.clicked.connect(self.openFileNameDialogLC)
        elif extension == ".out":
            submitField.clicked.connect(self.openFileNameDialogOutputFile)
        else:
            submitField.clicked.connect(self.openFileNameDialogRGB)
        
        # submitField.clicked.connect(self.openFileNameDialog)
        
        #Add status of loading the file.   
        if extension == ".pts":
            messageStatus =self.label_status_PC
        elif extension == ".json":
            messageStatus = self.label_status_LC
        elif extension == ".out":
            messageStatus = self.label_status_out 
            
        else:
            messageStatus = self.label_status_RGB
        
        
        # messageStatus = QLabel(statusMsg)
        messageStatus.setAlignment(Qt.AlignCenter)
        messageStatus.setWordWrap(True)

        #Add the button and file path to the form layout
        formLayout.addRow(messageLabel)
        formLayout.addRow(fileLabel, fileField)
        formLayout.addRow(submitField, messageStatus)
        # formLayout.addRow(messageStatus)

        #Add the form layout to the group box
        groupBox.setLayout(formLayout)
        self._verticalLayout.addWidget(groupBox, alignment=Qt.AlignCenter)
    
    #Check if we have all files to start the program.
    def fileCheck(self):
        if self.label_button_text_PC.text() != "" and self.label_button_text_LC.text() != "" and self.label_button_text_RGB.text() != "":
            self.createRecoloredPCwithLC.setEnabled(True)
            self.segmentPCwithLC.setEnabled(True)
            
            #Communicate that we have all the files ready to go. 
            # status = self.PCUtilTools.setFileNames(self.label_button_text_PC.text(), self.label_button_text_LC.text(), self.label_button_text_RGB.text())
            # self.loggingWrapper(status)
            
  
            
    #These are details only for the radio button associated with ranged recoloring of a point cloud. 
    #Of interest are the following:
    # Tell if we are active on changing by range. 
    #     self.activateRangedRecoloring   
    # For the colors:
    #     self.col1
    #     self.col2
    def addRadioButtonSelection(self):
        #This is the button and file path shower. 
        groupBox = QGroupBox()
        groupBox.setFixedWidth(350)
        formLayout = QFormLayout()
        # self.radioRecolorBut.toggled.connect(self.toggleRadioButton)
        # self.radioRecolorBut.setAlignment(Qt.AlignCenter)
        self.left_button = QRadioButton("Recolor Points")
        self.right_button = QRadioButton("Remove Points")
        self.left_button.toggled.connect(self.linMode)
        self.right_button.toggled.connect(self.bezierMode)
        self.checkbox_change_mode = QCheckBox("Use Spherical Selection")
        self.checkbox_grey_removal = QCheckBox("Remove Grey")
        
        helpBox = QLabel("Choose to recolor or remove points that are within the bounds of a bounding box in color space set by user. Using spherical estimation uses a spehrical median estimate and does not use a bounding box.")
        helpBox.setWordWrap(True)
        helpBox.setAlignment(Qt.AlignCenter)
        
        #Buttons for selecting start and end of the range of colors.
        # self.colorButton1 = QPushButton('Color 1', self)
        # self.colorButton1.setToolTip('Opens color dialog for color 1')
        # self.colorButton1.clicked.connect(self.onButtonColor1)
        
        # self.colorButton2 = QPushButton('Color 2', self)
        # self.colorButton2.setToolTip('Opens color dialog for color 2')
        # self.colorButton2.clicked.connect(self.onButtonColor2)
        
        
        #Target Color Selector
        self.colorButton3 = QPushButton('Select Bounding Box Colors', self)
        self.colorButton3.setToolTip('Occasionally, the median of a color will be outside the target of the majority of colors. This is a fall-back color used instead of the median of the population of points.')
        self.colorButton3.clicked.connect(self.onButtonColor3)
        
        
         
        self.colorEntry = QLineEdit("Use this line for RGB/HEX colors used in replacement.")
        self.intervalsEntry = QLineEdit("Enter # of intervals")
        self.targetColorsEntry = QLineEdit("If required, enter a target color for fall-back.")
        
        # self.colorButton1.setEnabled(False)
        # self.colorButton2.setEnabled(False)
        # self.colorButton3.setEnabled(False)
        self.colorEntry.setEnabled(False)
        self.targetColorsEntry.setEnabled(False)
        
        
        self.checkbox_grey_removal.setEnabled(False)
        # self.checkbox_change_mode.setEnabled(False)
        # self.linearGradientTwoTone.setEnabled(False)
        # self.bezierInterpolation.setEnabled(False)
        # self.hexList = QLineEdit("Enter as format: #000000 #FFFFFF")
         
        #End formatting of the layout
        # formLayout.addRow(self.radioRecolorBut)
        formLayout.addRow(helpBox)
        formLayout.addRow(self.left_button,self.right_button)
        formLayout.addRow(self.checkbox_change_mode,self.colorButton3)
        
        
        # formLayout.addRow(self.checkbox_grey_removal,self.checkbox_change_mode)
        
        # formLayout.addRow(self.colorEntry)
        # formLayout.addRow(self.targetColorsEntry)
        # formLayout.addRow(self.intervalsEntry)
        # formLayout.addRow(self.colorButton1,self.colorButton2)
        
        groupBox.setLayout(formLayout)
        self._verticalLayout.addWidget(groupBox, alignment=Qt.AlignCenter)
    
    #Used on button click to open the color dialog.
    def onButtonColor1(self):
        self.col1 = self.openColorDialog()
        self.recolor_QPushButton(self.colorButton1, self.col1 )
        colors = self.col1.getRgb()
        self.PCUtilTools.set_color_1([colors[0], colors[1], colors[2]])
        
    #Used on Button 2
    def onButtonColor2(self):
        self.col2 = self.openColorDialog()
        self.recolor_QPushButton(self.colorButton2, self.col2 )
        colors = self.col2.getRgb()
        self.PCUtilTools.set_color_2([colors[0], colors[1], colors[2]])
        
    def onButtonColor3(self):
        self.PCUtilTools.call_3DViewer()
        
        # self.col3 = self.openColorDialog()
        # self.recolor_QPushButton(self.colorButton3, self.col3 )
        # colors = self.col3.getRgb()
        # self.PCUtilTools.set_color_3([colors[0], colors[1], colors[2]])

    #This selects a color from a color map and sends it back
    def openColorDialog(self):
        color = QColorDialog.getColor()
        if color.isValid():
            print(color.name())
        return color   
        
    def setColorStringHex(self,color_string):
        self.PCUtilTools.set_list_hex_colors(color_string)      
        
    def setColorStringRGB(self,color_string):
        self.PCUtilTools.set_list_rgb_colors(color_string) 
        
    def linMode(self):
        self.setModeColoring("recolor")
        
        
    # Adding in the functionality. 
    def bezierMode(self):
        if (not self.checkbox_change_mode.isChecked()):
            self.setModeColoring("deletion_box") 
        else:
            self.setModeColoring("deletion_sphere") 
        
            
    #Set button behaviors    
    def setModeColoring(self,strIn):
        self.checkbox_grey_removal.setEnabled(True)
        self.checkbox_change_mode.setEnabled(True)
        self.colorButton3.setEnabled(True)
        if strIn == "linear":
            self.colorMode = "linear"
            self.colorEntry.setEnabled(False)
            self.targetColorsEntry.setEnabled(False)
            self.recolorWithRange.setEnabled(True)
            # self.colorButton1.setEnabled(True)
            # self.colorButton2.setEnabled(True)
            
        if strIn == "bezier":
            self.colorMode = "bezier"
            self.colorEntry.setEnabled(True)
            self.targetColorsEntry.setEnabled(True)
            # self.colorButton1.setEnabled(False)
            # self.colorButton2.setEnabled(False)
            self.recolorWithRange.setEnabled(True)
            
        if strIn == "recolor":
            self.colorMode = "recolor"
            self.targetColorsEntry.setEnabled(True)
            self.recolorWithRange.setEnabled(True)
            
        if strIn == "deletion_box" :
            self.colorMode = "deletion"
            self.targetColorsEntry.setEnabled(True)
            self.recolorWithRange.setEnabled(True)
        
        if strIn == "deletion_sphere" :
            self.colorMode = "deletion"
            self.targetColorsEntry.setEnabled(True)
            self.recolorWithRange.setEnabled(True)
            
            
    #Simple function to toggle between active and not active.
    def toggleRadioButton(self):
        if self.activateRangedRecoloring:
            self.activateRangedRecoloring = False
            #Need to set this selection on in order to avoid confusion.
            # self.colorButton1.setEnabled(False)
            # self.colorButton2.setEnabled(False)
            # self.recolorWithRange.setEnabled(False)
            self.left_button.setEnabled(False)
            self.right_button.setEnabled(False)
            self.colorEntry.setEnabled(False)
            
        else:
            self.checkbox_grey_removal.setEnabled(True)
            self.activateRangedRecoloring = True
            self.left_button.setEnabled(True)
            self.right_button.setEnabled(True)
            if (self.colorEntry.text != "Enter as format: 0,0,0 1,2,3  OR #000000 #FFFFFF"):
                self.colorEntry.setEnabled(True)
        
    #These are functions associated with the point cloud file selectors. 
    #This one handles the point cloud file.
    def openFileNameDialogPC(self):
        extension = ".pts"
        
        pathOut = os.path.join(self.localDir, self.inPointCloudDir)
        # if self.accessedPC == False:
        try:
            os.chdir(pathOut)
        except FileNotFoundError:
            os.mkdir(pathOut)
            os.chdir(pathOut)
            # self.accessedPC = True
        
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Open Point Cloud Data", pathOut,"PTS Files (*.pts);;PLY Files (*.ply);;PCD Files (*.pcd);;XYZ Files (*.xyz);;XYZN Files (*.xyzn);;XYZRGB Files (*.xyzrgb);;LAS Files (*.las);;LAZ Files (*.laz);;All Files (*)", options=options)
        statusMsg = "User cancelled operation or no file selected."
        label_mnger = self.label_status_PC

        
        if fileName and filename != "":
            line = fileName.split("/")
            name = line[len(line)-1]
            extension = name.split(".")[1]
            
            # temp ='(?:% s)' % '|'.join(self.pointcloud_extensions)
            # print(temp)
            
            if(extension in self.pointcloud_extensions):
            # if (extension not in fileName):
                statusMsg = "Error: File is not a valid file"
                fileName = ""
                self.recolor_QLabel(label_mnger, QColor(102,0,0),255)
            else:
                statusMsg = "File selected."
                self.label_field_file_name.setText(name)
                self.recolor_QLabel(label_mnger, QColor(0,51,25),255)
                self.loggingWrapper(self.PCUtilTools.load_point_cloud(fileName))
            # print(fileName)
        self.label_button_text_PC.setText(fileName)        
        label_mnger.setText(statusMsg)
        self.fileCheck()
        self.exportPCConversion.setEnabled(True)
            
    #This one handles the label file.
    def openFileNameDialogLC(self):
        extension = ".json"
        
        pathOut = os.path.join(self.localDir, self.inLabelCloudDir)
        # if self.accessedLC == False:
        try:
            os.chdir(pathOut)
        except FileNotFoundError:
            os.mkdir(pathOut)
            os.chdir(pathOut)
            # self.accessedLC = True
        
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Open labelCloud file", pathOut,"JSON Files (*.json);;All Files (*)", options=options)
        statusMsg = "User cancelled operation or no file selected."
        label_mnger = self.label_status_LC
        
        if fileName and filename != "":
            if (extension not in fileName):
                statusMsg = "Error: File is not a " + extension + " file"
                fileName = ""
                self.recolor_QLabel(label_mnger, QColor(102,0,0),255)
            else:
                statusMsg = "File selected."
                self.recolor_QLabel(label_mnger, QColor(0,51,25),255)
                self.loggingWrapper(self.PCUtilTools.load_labelCloud(fileName))
            # print(fileName)
        self.label_button_text_LC.setText(fileName)        
        label_mnger.setText(statusMsg)
        self.fileCheck()
   
    #This one handles the RGB file text notes.
    def openFileNameDialogRGB(self):
        extension = ".txt"
        
        pathOut = os.path.join(self.localDir, self.inRgbDataDir)
        # if self.accessedRGB == False:
        try:
            os.chdir(pathOut)
        except FileNotFoundError:
            os.mkdir(pathOut)
            os.chdir(pathOut)
            # self.accessedRGB = True
            
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Open RGB Selected Labels", pathOut,"Text Files (*.txt);;All Files (*)", options=options)
        statusMsg = "User cancelled operation or no file selected."
        label_mnger = self.label_status_RGB
        
        if fileName and filename != "":
            if (extension not in fileName):
                statusMsg = "Error: File is not a " + extension + " file"
                fileName = ""
                self.recolor_QLabel(label_mnger, QColor(102,0,0),255)
            else:
                statusMsg = "File selected."
                self.recolor_QLabel(label_mnger, QColor(0,51,25),255)
                #TODO: Move the function to load the file immediately to here. 
                self.loggingWrapper(
                    self.PCUtilTools.load_rgbCloud(fileName)
                )
                
                # self.loggingWrapper("RGB file loaded successfully.")
            # print(fileName)
        self.label_button_text_RGB.setText(fileName)        
        label_mnger.setText(statusMsg)
        self.fileCheck()
    
    
        #This one handles the label file.
   
    def openFileNameDialogOutputFile(self):
        extension = ".pts"
        
        pathOut = os.path.join(self.localDir, self.inLabelCloudDir)
        try:
            os.chdir(pathOut)
        except FileNotFoundError:
            os.mkdir(pathOut)
            os.chdir(pathOut)
        
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, filter = QFileDialog.getSaveFileName(self,"Set output file", pathOut,"PTS Files (*.pts);;PLY Files (*.ply);;PCD Files (*.pcd);;XYZ Files (*.xyz);;XYZN Files (*.xyzn);;XYZRGB Files (*.xyzrgb);;LAS Files (*.las);;LAZ Files (*.laz);;All Files (*.)", options=options)
        statusMsg = "User cancelled operation or no file selected."
        label_mnger = self.label_status_out
        print(fileName)
        name = filter.split(".")
        name = name[1].replace(")","")
        fileName += "." + name
        print(fileName)
        if fileName and fileName != "":
            if (extension not in fileName):
                # statusMsg = "Error: File is not a " + extension + " file"
                # fileName = ""
                self.recolor_QLabel(label_mnger, QColor(102,0,0),255)
            else:
                statusMsg = "Output location declared."
                self.recolor_QLabel(label_mnger, QColor(0,51,25),255)
                
                # self.loggingWrapper(self.PCUtilTools.load_labelCloud(fileName))
            # print(fileName)
        self.label_field_file_name.setText(fileName)        
        label_mnger.setText(statusMsg)
        # self.fileCheck()

if (__name__ == '__main__'):
    application = QApplication([])
    mainWindow = MainWindow()
    mainWindow.show()
    application.exec_()