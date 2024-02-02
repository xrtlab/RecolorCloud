import numpy as np


import matplotlib
# matplotlib.use('Qt5Agg')

# print (matplotlib.rcParams.keys())
# matplotlib.rcParams['backend.qt5']='PyQt5'

import matplotlib.pyplot as plt 
from matplotlib.widgets import TextBox
from matplotlib.widgets import Button



class Bounding_Box_selector:
    min_user_input  =np.array([0.,0.,0.]).astype(np.float64)
    max_user_input  =np.array([0.,0.,0.]).astype(np.float64)
    
    #First two points are used for declaring the bounding box
    user_colors_bbox = np.array([[0,0],[0,0],[0,0]]).astype(np.float64)


    #We need an optional array to plot incoming colors from 
    def __init__(self, x_list =[], y_list =[], z_list =[] ): 
        print("Initializing Bounding Box Selector")
        fig = plt.figure()
        self.ax = fig.add_subplot(111, projection='3d')
        self.ax.set_xlabel('Red axis', color='r')
        self.ax.set_ylabel('Green axis', color='g')
        self.ax.set_zlabel('Blue axis', color='b')
        
        self.ax.tick_params(axis='x', colors='r')
        self.ax.tick_params(axis='y', colors='g')
        self.ax.tick_params(axis='z', colors='b')     
        
        self.ax.spines['bottom'].set_color('r')
        self.ax.spines['top'].set_color('r')
        self.ax.spines['left'].set_color('g')
        self.ax.spines['right'].set_color('g')
        
        fig.canvas.set_window_title('Bounding Box Selector')
        
        self.ax.set_xlim(0, 256)
        self.ax.set_ylim(0, 256)
        self.ax.set_zlim(0, 256)
        self.ax.view_init(elev=30 , azim=-135)
        
        # self.r_list = [45,55,1]
        # self.g_list = [64,55,74]
        # self.b_list = [25,55,35]
        self.r_list = x_list
        self.g_list = y_list
        self.b_list = z_list
        
        # print(len(self.r_list))
        # self.scatter_plot = self.ax.scatter(self.r_list,self.b_list,self.g_list,c='r',marker='o')
        
        # print()
        
        for pt in range(0,len(self.r_list)): #Should be the same to keep it functional
            # print((self.r_list[pt],self.g_list[pt],self.b_list[pt]))
            color_point = (self.r_list[pt]/255,self.g_list[pt]/255,self.b_list[pt]/255)
            self.ax.scatter(self.r_list[pt],self.b_list[pt],self.g_list[pt],color=color_point,marker='o')
        
        color_point = (self.user_colors_bbox[0][0]/255,self.user_colors_bbox[1][0]/255,self.user_colors_bbox[2][0]/255)
        self.scatter_1 = self.ax.scatter(self.user_colors_bbox[0],self.user_colors_bbox[1],self.user_colors_bbox[2],color=color_point,marker='o',edgecolors='k')
        self.text_1 = self.ax.text(self.user_colors_bbox[0][0],self.user_colors_bbox[1][0],self.user_colors_bbox[2][0],f'({self.user_colors_bbox[0][0]},{self.user_colors_bbox[1][0]},{self.user_colors_bbox[2][0]})',color=color_point)
        
        color_point = (self.user_colors_bbox[0][1]/255,self.user_colors_bbox[1][1]/255,self.user_colors_bbox[2][1]/255)
        self.scatter_2 = self.ax.scatter(self.user_colors_bbox[0],self.user_colors_bbox[1],self.user_colors_bbox[2],color=color_point,marker='o',edgecolors='k')
        self.text_2 = self.ax.text(self.user_colors_bbox[0][1],self.user_colors_bbox[1][1],self.user_colors_bbox[2][1],f'({self.user_colors_bbox[0][1]},{self.user_colors_bbox[1][1]},{self.user_colors_bbox[2][1]})',color=color_point)
        
        
        self.update_bounding_box(self.user_colors_bbox )
        
        projections = []
        ax3d = fig.gca(projection='3d')
                
        w_box = 0.055
        h_box = 0.075
        origin = 0.06
        
        ax_button     = plt.axes([0.005 , 0.0, w_box*5, h_box])

        ax_box_R_min  = fig.add_axes([origin, h_box*2, w_box, h_box])
        ax_box_G_min  = fig.add_axes([origin + w_box, h_box*2, w_box, h_box])
        ax_box_B_min  = fig.add_axes([origin + (w_box*2),h_box*2, w_box, h_box])
        
        ax_box_R_max  = fig.add_axes([origin, h_box, w_box, h_box])
        ax_box_G_max  = fig.add_axes([origin + w_box, h_box, w_box, h_box])
        ax_box_B_max  = fig.add_axes([origin + (w_box*2),h_box, w_box, h_box])
        
        text_help = ("Select the two corners of the bounding box you want to use for the color detection.")
        plt.text(0.005, 0.95, text_help, fontsize=8, transform=plt.gcf().transFigure)
        
        
        color_box_r = [200/255,50/255,0/255]
        hover_color_r = [255/255,50/255,0/255]
        self.min_r = TextBox(ax_box_R_min, 'Min', initial='0',color=color_box_r,hovercolor=hover_color_r)
        self.min_r.on_submit(self.update_3D)
        
        color_box_g = [0/255,200/255,00/255]
        hover_color_g = [0/255,255/255,00/255]
        self.min_g = TextBox(ax_box_G_min, '', initial='0',color=color_box_g,hovercolor=hover_color_g)
        self.min_g.on_submit(self.update_3D)
        
        color_box_b = [0/255,50/255,200/255]
        hover_color_b = [0/255,50/255,255/255]
        self.min_b = TextBox(ax_box_B_min, '', initial='0',color=color_box_b,hovercolor=hover_color_b)
        self.min_b.on_submit(self.update_3D)
        
        self.max_r = TextBox(ax_box_R_max, 'Max', initial='0',color=color_box_r,hovercolor=hover_color_r)
        self.max_r.on_submit(self.update_3D)
        self.max_g = TextBox(ax_box_G_max, '', initial='0',color=color_box_g,hovercolor=hover_color_g)
        self.max_g.on_submit(self.update_3D)
        self.max_b = TextBox(ax_box_B_max, '', initial='0',color=color_box_b,hovercolor=hover_color_b)
        self.max_b.on_submit(self.update_3D)      
        b_submit = Button(ax_button, 'Confirm Bounding Box')
        b_submit.on_clicked(self.submit_vectors)
        
        
        print("Finished plotting")
        plt.show()
        
     
    def update_bounding_box(self,vecs):
        #[[x],[y],[z]]
        
        #Points organized as: P0, P1, P2, P3, P4, P5, P6, P7
        #P0 = [x_min,y_min,z_min]
        P0 = [vecs[0][0],vecs[1][0],vecs[2][0]]
        P1 = [vecs[0][1],vecs[1][1],vecs[2][1]]       
        P2 = [vecs[0][1],vecs[1][0],vecs[2][0]]
        P3 = [vecs[0][0],vecs[1][1],vecs[2][1]]
        P4 = [vecs[0][1],vecs[1][1],vecs[2][0]]
        P5 = [vecs[0][0],vecs[1][0],vecs[2][1]]
        P6 = [vecs[0][0],vecs[1][1],vecs[2][0]]
        P7 = [vecs[0][1],vecs[1][0],vecs[2][1]]
        sequence = [P0,P2,P4,P6,P0,P5,P7,P2,P4,P1,P7,P5,P3,P1,P3,P6]

        bbox_points =[[],[],[]]
        for point in sequence:
            bbox_points[0].append(point[0])
            bbox_points[1].append(point[1])
            bbox_points[2].append(point[2])
        
        self.plotted_lines =  self.ax.plot(bbox_points[0],bbox_points[1],bbox_points[2],color='b')
    
    def check_text_input(self,text):
        value = int(text)
        # print(value)
        if value < 0:
            value = 0
        elif value > 254:
            value = 254
        
        return value
        
        
    def update_3D(self,expression):
        self.min_user_input = np.array([self.check_text_input(self.min_r.text),self.check_text_input(self.min_g.text),self.check_text_input(self.min_b.text)]).astype(np.float64)
        self.max_user_input = np.array([self.check_text_input(self.max_r.text),self.check_text_input(self.max_g.text),self.check_text_input(self.max_b.text)]).astype(np.float64)
        
        
        # print(self.min_user_input)
        self.user_colors_bbox[0][0] = int(self.min_user_input[0])
        self.user_colors_bbox[1][0] = int(self.min_user_input[1])
        self.user_colors_bbox[2][0] = int(self.min_user_input[2])
        
        self.user_colors_bbox[0][1] = int(self.max_user_input[0])
        self.user_colors_bbox[1][1] = int(self.max_user_input[1])
        self.user_colors_bbox[2][1] = int(self.max_user_input[2])
        
  
        self.scatter_1.remove()
        self.scatter_2.remove()
        self.text_1.remove()
        self.text_2.remove()
        
        
        #Updates the labels and colors of the points
        color_point = (self.user_colors_bbox[0][0]/255,self.user_colors_bbox[1][0]/255,self.user_colors_bbox[2][0]/255)
        self.scatter_1 = self.ax.scatter(self.user_colors_bbox[0],self.user_colors_bbox[1],self.user_colors_bbox[2],color=color_point,marker='o',edgecolors='k')
        self.text_1 = self.ax.text(self.user_colors_bbox[0][0],self.user_colors_bbox[1][0],self.user_colors_bbox[2][0],f'({self.user_colors_bbox[0][0]},{self.user_colors_bbox[1][0]},{self.user_colors_bbox[2][0]})',color=color_point)

        color_point = (self.user_colors_bbox[0][1]/255,self.user_colors_bbox[1][1]/255,self.user_colors_bbox[2][1]/255)
        self.scatter_2 = self.ax.scatter(self.user_colors_bbox[0],self.user_colors_bbox[1],self.user_colors_bbox[2],color=color_point,marker='o',edgecolors='k')
        self.text_2 = self.ax.text(self.user_colors_bbox[0][1],self.user_colors_bbox[1][1],self.user_colors_bbox[2][1],f'({self.user_colors_bbox[0][1]},{self.user_colors_bbox[1][1]},{self.user_colors_bbox[2][1]})',color=color_point)

     
        l = self.plotted_lines.pop()
        l.remove()
        self.update_bounding_box(self.user_colors_bbox )
     
        
        
        self.ax.relim()
        self.ax.autoscale_view()
        plt.draw()
    
    #Close the window and return the bounding box vectors
    def submit_vectors(self,event):
        plt.close(1)
        # return self.min_user_input, self.max_user_input
    def get_vectors(self):
        return self.min_user_input, self.max_user_input