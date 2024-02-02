#Author: Esteban Segarra
#Purpose: This is the backend that manages the pointcloud operations. 
import math
import json 
import open3d
import numpy as np
import random
from scipy.spatial.transform import Rotation as R
from userGraphVisualizer import Bounding_Box_selector
import scipy.spatial.distance
from datetime import datetime
import laspy as lp
##############################################################################################################################

class PCTools_Utils:
    def __init__(self):
        #Variables for pointcloud manipulation
        self.pointcloud     = None
        self.pointcloudRaw  = None #This is just ASCII data
        self.labelCloudFile = []   #JSON File
        self.rgbCloudFile   = {}   #Dictionary with the colors per label and flag
        
        # self.transformation = np.array([ 20.0, -38.0, -5.60]).astype(np.float64)
        self.transformation = np.array([0,0,0]).astype(np.float64)
        
        #Used in RGB Range Recoloring
        self.rgbColor1 = [0.0,0.0,0.0]
        self.rgbColor2 = [1.0,1.0,1.0]
        self.center_median = np.array([0.,0.,0.]).astype(np.float64)
        self.using_target_median = False
        self.hex_colors = []
        self.rgb_colors = []
        
        #For use in gradient coloring
        self.replacement_colors = [] 
        
        #For use in deleting colors. 
        self.deletion_colors = []
        self.user_bbox_vector_min = np.array([0.,0.,0.]).astype(np.float64)
        self.user_bbox_vector_max = np.array([0.,0.,0.]).astype(np.float64)
        
        self.interval_colors = 50
        self.radius_of_sphere = 85.0 #Radius used to measure if in sphere or not
        self.status_runnable = [False,False,False]
        
        self.gray_deletion = False
        self.spherical_bounding = False
        self.color_threshold = 6.0
        self.gradient_colors = self.linear_gradient(self.rgbColor1,self.rgbColor2,n=self.interval_colors)
        
###############################################################################################
    #Function to recolor the point cloud and start the whole process 
    #Call this as the primary function
    def recolor_point_cloud(self):
        if self.status_runnable != [True,True,True]:
            print("Error: Files not loaded")
            pass
        
        #Local var
        boxes_geometry = []

        #Create Open3D bounding boxes
        for box in self.labelCloudFile:
            center   = np.asarray([
                box['centroid']['x'],
                box['centroid']['y'],
                box['centroid']['z']
                ]).astype(np.float64)
            rotation = np.asarray([
                box['rotations']['x'],
                box['rotations']['y'],
                box['rotations']['z'],        
                ]).astype(np.float64)
            extent   = np.asarray([
                box['dimensions']['length'],
                box['dimensions']['width'],
                box['dimensions']['height'],
                ]).astype(np.float64)
            matrix_converted = R.from_euler('xyz',rotation).as_matrix()
            bbox = self.create_bounding_box(center,matrix_converted,extent)

            #Need to call as a dictionary here..
            bbox.color =  np.asarray(self.rgbCloudFile[box['name'].lower()][0]).astype(np.float64)
            #If the flag is set to 1, then the box is active
            if self.rgbCloudFile[box['name'].lower()][1][0] == "1":
                boxes_geometry.append(bbox)
        
        drawn_geometry = []
        for bound in boxes_geometry:
            drawn_geometry.append(bound)
        drawn_geometry.append(self.pointcloud)
        open3d.visualization.draw_geometries(drawn_geometry)
        
        #Calculate the center of the point cloud relative to how labelCloud centers the bboxes
        # c = self.calc_center(self.pointcloud)
        # c = np.asarray(c).astype(np.float64)
        # c = self.transformation
        #Move the point cloud to the bounding boxes
        # self.pointcloud.translate(c) 
        
        # open3d.visualization.draw_geometries(drawn_geometry)
        
        ##For cropping the cloud and recoloring the point clouds
        self.cropped_clouds = []
        for bound in boxes_geometry:
            cloud_out = self.pointcloud.crop(bound)
            col = (bound.color.astype(np.float64)/255.0)
            cloud_out.paint_uniform_color(col)
            self.cropped_clouds.append(cloud_out)
            
        open3d.visualization.draw_geometries(self.cropped_clouds)       
 
    def segment_point_cloud(self):        
        if self.status_runnable != [True,True,True]:
            print("Error: Files not loaded")
        pass
        
        #Local var
        boxes_geometry = []
        
        #Move the point cloud to the bounding boxes
        # transformation = np.array([ 20.0, -38.0, -6]).astype(np.float64)
        self.pointcloud.translate(self.transformation) 

        #Create Open3D bounding boxes
        for box in self.labelCloudFile:
            center   = np.asarray([
                box['centroid']['x'],
                box['centroid']['y'],
                box['centroid']['z']
                ]).astype(np.float64)
            rotation = np.asarray([
                box['rotations']['x'],
                box['rotations']['y'],
                box['rotations']['z'],        
                ]).astype(np.float64)
            extent   = np.asarray([
                box['dimensions']['length'],
                box['dimensions']['width'],
                box['dimensions']['height'],
                ]).astype(np.float64)
            matrix_converted = R.from_euler('xyz',rotation).as_matrix()
            bbox = self.create_bounding_box(center,matrix_converted,extent)

            #Need to call as a dictionary here..
            bbox.color =  np.asarray(self.rgbCloudFile[box['name'].lower()][0]).astype(np.float64)
            #If the flag is set to 1, then the box is active
            if self.rgbCloudFile[box['name'].lower()][1][0] == "1":
                boxes_geometry.append(bbox)
        
        ##For cropping the cloud and recoloring the point clouds
        self.cropped_clouds = []
        for bound in boxes_geometry:
            cloud_out = self.pointcloud.crop(bound)
            self.cropped_clouds.append(cloud_out)
            
        open3d.visualization.draw_geometries(self.cropped_clouds)
    
    def range_recolor_point_cloud(self):        
        if self.status_runnable != [True,True,True]:
            print("Error: Files not loaded")
            pass          
        
        #Local var
        boxes_geometry = []
        
        #Start
        start_time = datetime.now()
        
        #Move the point cloud to the bounding boxes
        self.pointcloud.translate(self.transformation) 

        #Create Open3D bounding boxes
        for box in self.labelCloudFile:
            center   = np.asarray([
                box['centroid']['x'],
                box['centroid']['y'],
                box['centroid']['z']
                ]).astype(np.float64)
            rotation = np.asarray([
                box['rotations']['x'],
                box['rotations']['y'],
                box['rotations']['z'],        
                ]).astype(np.float64)
            extent   = np.asarray([
                box['dimensions']['length'],
                box['dimensions']['width'],
                box['dimensions']['height'],
                ]).astype(np.float64)
            matrix_converted = R.from_euler('xyz',rotation).as_matrix()
            bbox = self.create_bounding_box(center,matrix_converted,extent)

            #Need to call as a dictionary here..
            box_name = self.rgbCloudFile[box['name'].lower()][0]            
            bbox.color =  np.asarray(box_name).astype(np.float64)

            #If the flag is set to 1, then the box is active for recoloring
            if self.rgbCloudFile[box['name'].lower()][1][0] == "1":
                boxes_geometry.append(bbox)
        
        ##For cropping the cloud and recoloring the point clouds
        self.cropped_clouds = []
        point_cloud_crops = self.pointcloud
        indices_to_crop = []
        print(len(boxes_geometry))
        counter_boxes = 1
        
        print("Starting recoloring")
        for bound in boxes_geometry:
            bb_time_start_ = datetime.now()
            c_cloud_selection = point_cloud_crops.crop(bound)    
            
            #This should access all the points in the cloud and recolor them
            pts = np.asarray(c_cloud_selection.points)
            cols = np.asarray(c_cloud_selection.colors)
            delete_indexes = []
            
            #First option should be to recolor by bounding box
            if (not self.spherical_bounding):        
                # print("Recoloring by bounding box")
                if (self.recoloring_mode == "recolor"):                 
                    c_cloud_selection = self.recolor_points_and_keep_by_bbox(self.user_bbox_vector_min,self.user_bbox_vector_max,cols,c_cloud_selection)
                    
                    
                elif (self.recoloring_mode == "deletion_box"):
                    transformed_colors = cols * 255
                    #Convert colors to str
                    str_original_colors = []
                    for col in transformed_colors:
                        str_original_colors.append(str(col))
                    
                    
                    #input colors have to be in the range of 0-255
                    keep_colors,deletable_colors = self.points_inside_bbox(self.user_bbox_vector_min,self.user_bbox_vector_max,transformed_colors) 
                    
                    str_keep_colors = []
                    for col in deletable_colors:
                        delete_indexes.append(str_keep_colors.append(str(col)))

                    # print(deletable_colors)
                    delete_indexes = np.where(np.isin(str_original_colors,str_keep_colors))
                    # print(delete_indexes)
                    #We need to remove the points from the selected point cloud
                    c_cloud_selection = c_cloud_selection.select_by_index(delete_indexes[0],True)
                    
                elif(self.recoloring_mode == "deletion_sphere"):
                    c_cloud_selection = self.spherical_selection_deletion(cols,c_cloud_selection)
            else:
                #Keeping old code for spehrical estimation.
                print("Spherical recoloring")
                c_cloud_selection = self.spherical_selection_recolor(cols,c_cloud_selection)
                
                
            # elif(self.recoloring_mode == "gradient_replacement"):
            #     grad_color_list = self.polylinear_gradient(self.replacement_colors,self.interval_colors)
            #     #Uniformly replaces all points in the cloud with colors given within a range by the user. 
            #     for pt in range(len(pts)): 
            #         #Because it is cursed to change the colors based on pure RGB, transform to float. 
            #         c_cloud_selection.colors[pt] = self.generate_random_gradient_color(grad_color_list)
            
            self.cropped_clouds.append(c_cloud_selection)
            
            #Cut out the outside bounds from where we just recolored the PC.
            indices_bound = bound.get_point_indices_within_bounding_box(self.pointcloud.points)
            indices_to_crop.extend(indices_bound)
            
            #Timestamping 
            bb_end_time = datetime.now()
            print("Time to process box " + str(counter_boxes) + " with " +  str(len(indices_bound)) + " points recolored: "  + str(bb_end_time - bb_time_start_))
            counter_boxes += 1

        drawn_geometry = []
        for bound in boxes_geometry:
            drawn_geometry.append(bound)
        drawn_geometry.append(self.pointcloud)
        open3d.visualization.draw_geometries(drawn_geometry)

        point_cloud_cropped = self.pointcloud.select_by_index(indices_to_crop,True)
        # open3d.visualization.draw_geometries([point_cloud_cropped])
        self.cropped_clouds.append(point_cloud_cropped)
        
        print("Time to process recoloring: " + str(datetime.now() - start_time))
        open3d.visualization.draw_geometries(self.cropped_clouds)

    def downsample_point_cloud(self, downsample_type = 1, percentage_downsample = 0.1):
        """! This is the function that downsamples the point cloud. It takes in the type of downsampling to be done.

        Args:
            downsample_type (_type_): _description_
        """
        self.cropped_clouds = []
        fartherst_point_sampling = 4
        voxel_size = 0.05
        
        if (self.pointcloud == None):
            print("Error: Point cloud not loaded")
            return
        
        if(downsample_type == 0): #Voxel downsampling
            self.cropped_clouds.append(self.pointcloud.voxel_down_sample(voxel_size)) 
        elif (downsample_type == 1):
            ref_size = np.asarray(self.pointcloud.points).shape[0] #Get the size of the array    
            points_by_percentage = int(ref_size * percentage_downsample)
            factor_downsample = int(ref_size/points_by_percentage)
            self.cropped_clouds.append(self.pointcloud.uniform_down_sample(factor_downsample)) #Downsample the point cloud by 10%
            
        elif (downsample_type == 2):
            self.cropped_clouds.append(self.pointcloud.farthest_point_sampling(fartherst_point_sampling))
            
        elif (downsample_type == 3):
            self.cropped_clouds.append(self.pointcloud.random_down_sample(percentage_downsample))
        else:
            print("Error: Downsample type not found")
        
        
        
    def generate_PC(self,file_location):
        """"! This is the function that generates the point cloud. It takes in the location of the point cloud and the location of the output file."""
        self.IO.load_point_cloud(file_location) #Load the point cloud
        PC = self.IO.get_pc_data() #Get the point cloud data
             
        #Get the size of the np array
        ref_size = np.asarray(PC.points).shape[0] #Get the size of the array        
        factor_downsample = int(ref_size/self.max_pts_downscaling)
        self.out_PC = PC.uniform_down_sample(factor_downsample) #Downsample the point cloud by 10%

    def call_3DViewer(self):
        if self.status_runnable != [True,True,True]:
            print("Error: Files not loaded")
            return
        
        #Local var
        boxes_geometry = []

        #Move the point cloud to the bounding boxes
        # self.pointcloud.translate(self.transformation) 

        #Create Open3D bounding boxes
        for box in self.labelCloudFile:
            center   = np.asarray([
                box['centroid']['x'],
                box['centroid']['y'],
                box['centroid']['z']
                ]).astype(np.float64)
            rotation = np.asarray([
                box['rotations']['x'],
                box['rotations']['y'],
                box['rotations']['z'],        
                ]).astype(np.float64)
            extent   = np.asarray([
                box['dimensions']['length'],
                box['dimensions']['width'],
                box['dimensions']['height'],
                ]).astype(np.float64)
            matrix_converted = R.from_euler('xyz',rotation).as_matrix()
            bbox = self.create_bounding_box(center,matrix_converted,extent)

            #Need to call as a dictionary here..
            box_name = self.rgbCloudFile[box['name'].lower()][0]            
            bbox.color =  np.asarray(box_name).astype(np.float64)

            #If the flag is set to 1, then the box is active for recoloring
            if self.rgbCloudFile[box['name'].lower()][1][0] == "1":
                boxes_geometry.append(bbox)
        
        ##For cropping the cloud and recoloring the point clouds
        self.cropped_clouds = []
        point_cloud_crops = self.pointcloud
        print(len(boxes_geometry))

        #Get all the colors in the boxes and return the spectrum.
        full_color_spectrum = np.array([[0,0,0]])
        count = 0   
        
        for bound in boxes_geometry:
            c_cloud_selection = point_cloud_crops.crop(bound)    
            cols = np.asarray(c_cloud_selection.colors)
            u_cols = np.unique(cols,axis=0)
            full_color_spectrum = np.concatenate((full_color_spectrum,u_cols))
            print(count)
            count += 1
            
        #Clean out any duplicates
        full_color_spectrum = np.unique(full_color_spectrum,axis=0)*255
        full_color_spectrum = np.delete(full_color_spectrum,0,0) #Delete our starting point
        
        #Bounding the colors in the bounding box. 
        down_sample = [[],[],[]]
        total_len = full_color_spectrum.shape[0]
        total_steps = 32
        
        for i in range(0,total_steps):
            index = math.floor(i * (total_len/total_steps))
            if index > total_len:
                index = total_len-1
            down_sample[0].append(full_color_spectrum[index][0])
            down_sample[1].append(full_color_spectrum[index][1])
            down_sample[2].append(full_color_spectrum[index][2])
        full_color_spectrum = [[0,0,0]]
     
        print("Starting Visualizer")
        self.BBox_Viewer = Bounding_Box_selector(down_sample[0],down_sample[1],down_sample[2])
        self.user_bbox_vector_min,self.user_bbox_vector_max = self.BBox_Viewer.get_vectors()
        print("Ending Visualizer")

    def get_vectors_bbox(self):
        self.user_bbox_vector_min,self.user_bbox_vector_max = self.BBox_Viewer.get_vectors()


    def generate_random_gradient_color(self,grad_color_list):
        col =  grad_color_list[random.randint(0,len(grad_color_list)-1)]
        col = np.asarray(col)
        col = (col.astype(np.float64)/255.0)
        return col
    
    #Deletion strategy. 
    def spherical_selection_deletion(self,cols,c_cloud_selection):
        #By some general idea, if we have all green zots, we could encompass the mayority using the median
        center_cluster = np.median(cols.reshape(-1,3),axis=0)
        cols_unique = np.unique(cols,axis=0)
        outlier_colors = []
        palette_colors = [] 
        
        #Arbritary threshold for the color distance
        if (self.calculate_dist_3d_two_points(self.center_median,center_cluster) > 60.0 and self.using_target_median):
            center_cluster = self.center_median
        
        #Find all the unique colors and create two lists, one with colors that can be used later for recoloring
        # and the other colors that are not within threshold to be replaced
        for col in cols_unique:                    
            if (self.is_in_sphere(self.radius_of_sphere,center_cluster*255,col*255)):
                palette_colors.append(col)
            else:
                outlier_colors.append(str(col))
                
        colors_to_check = []
        for col in cols:
            colors_to_check.append(str(col))
        
        #This will cut down the amount of points to look at by only looking at the points that are outside the palette
        delete_indexes = np.where(np.isin(colors_to_check,outlier_colors)) #not going to work if cols is not in str format...
        c_cloud_selection = c_cloud_selection.select_by_index(delete_indexes[0],True)
        return c_cloud_selection
    
    
    
    
###############################################################################################
## Spherical selection functions
    def spherical_selection_recolor(self,cols,c_cloud_selection):
        #By some general idea, if we have all green zots, we could encompass the mayority using the median
        center_cluster = np.median(cols.reshape(-1,3),axis=0)
        cols_unique = np.unique(cols,axis=0)
        colors_to_repaint = []
        palette_colors = [] 
        
        #Arbritary threshold for the color distance
        if (self.calculate_dist_3d_two_points(self.center_median,center_cluster) > 60.0 and self.using_target_median):
            center_cluster = self.center_median
        
        #Find all the unique colors and create two lists, one with colors that can be used later for recoloring
        # and the other colors that are not within threshold to be replaced
        for col in cols_unique:                    
            if (self.is_in_sphere(self.radius_of_sphere,center_cluster*255,col*255)):
                palette_colors.append(col)
            else:
                colors_to_repaint.append(str(col))
        # print("Finished Pallete")
        
        colors_to_check = []
        for col in cols:
            colors_to_check.append(str(col))
        
        #This will cut down the amount of points to look at by only looking at the points that are outside the palette
        indexes_colors_to_repaint = np.where(np.isin(colors_to_check,colors_to_repaint)) #not going to work if cols is not in str format...
        # print("Finished Indexing Colors")
        for index in indexes_colors_to_repaint[0]:
            closest_color =  palette_colors[random.randint(0,len(palette_colors)-1)]
            c_cloud_selection.colors[index] = closest_color
        return c_cloud_selection
    
    
    
        # #Check for all points - keeping for future bad reference 
        # for pt in range(len(pts)): 
        #     #Radius will be for around 1/2 of the RGB space
        #     col = c_cloud_selection.colors[pt] *255      
                    
        #     if (str(col) in colors_to_repaint):
        #         #Find the closest color in the palette
        #         closest_color =  palette_colors[random.randint(0,len(palette_colors)-1)]
        #         c_cloud_selection.colors[pt] = closest_color
        # print("Finished Recoloring")
    
    def is_in_sphere(self,radius,center,test_point):
        dist = math.sqrt(math.pow(test_point[0] - center[0],2) 
                         + math.pow(test_point[1] - center[1],2)
                         + math.pow(test_point[2] - center[2],2)
                         )
        #If distance is greater than radius, then it is outside the sphere
        return dist < radius

    def calculate_dist_3d_two_points(self,p1,p2):
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)
###############################################################################################
    ###### Bounding Box selection functions
    #Returns an array with unique colors respectively moved to recolor them. 
    def recolor_points_and_keep_by_bbox(self,vector_1_user,vector_2_user, array_of_colors,c_cloud_selection):
        array_of_colors = array_of_colors * 255
        array_of_unique_colors = np.unique(array_of_colors,axis=0)
        
        #Find the corners of a 3d bounding box
        extrema_vector_min,extrema_vector_max = self.check_distance_and_get_max_min(array_of_unique_colors,[255.,255.,255.],[0.,0.,0.])
        
        #Generate the size and scaling factor relative to the user bbox
        box_rays_user       = np.abs(vector_1_user - vector_2_user)
        box_rays_all_colors = np.abs(extrema_vector_max - extrema_vector_min)
        scaling_factor = box_rays_user / box_rays_all_colors
        
        #Find the centroid of the user bbox and the centroid of the colors
        centroid_user       = np.asarray([vector_1_user[0] + vector_2_user[0],vector_1_user[1] + vector_2_user[1],vector_1_user[2] + vector_2_user[2]]) / 2
        centroid_all_colors = np.asarray([extrema_vector_max[0] + extrema_vector_min[0],extrema_vector_max[1] + extrema_vector_min[1],extrema_vector_max[2] + extrema_vector_min[2]]) / 2
        
        #Find the translation vector
        transform_vector = centroid_user - centroid_all_colors      
        
        #New colors
        recolored_colors = np.round((array_of_colors * scaling_factor + transform_vector),0)/255
        c_cloud_selection.colors = open3d.utility.Vector3dVector(recolored_colors) 

        #Recolor the points and send out as the recolored values. Needs to be at most the nearest whole integer then converted back to float
        return c_cloud_selection

    def check_distance_and_get_max_min(self,array_of_points,point_max,point_min):
        min_vec = np.array(point_min)
        max_vec = np.array(point_max)
        dist_min = -9999
        dist_max = 9999
        for pt in array_of_points:
            dist_min_t = self.calculate_dist_3d_two_points(pt,min_vec)
            if (dist_min_t <= dist_min):
                dist_min = dist_min_t
                min_vec = pt
                continue #If we found a new min, we don't need to check the max
            dist_max_t = self.calculate_dist_3d_two_points(pt,max_vec)
            if (dist_max_t >= dist_max):
                dist_max = dist_max_t
                max_vec = pt
                continue
        return min_vec,max_vec 
        
    def recolor_points_and_delete_by_bbox(self,vector_1_user,vector_2_user, array_of_colors):
        pass

    #Checks if points are inside or outside a bounding box. Converts to string for ease of use
    def points_inside_bbox(self,vector_1,vector_2, array_of_points):
        exterior_points = []
        interior_points = []
        for pt in array_of_points:
            if (pt[0] > vector_1[0] and 
                pt[0] < vector_2[0] and 
                pt[1] > vector_1[1] and 
                pt[1] < vector_2[1] and 
                pt[2] > vector_1[2] and 
                pt[2] < vector_2[2]):
                interior_points.append(str(pt))
            else:
                exterior_points.append(str(pt))
        return interior_points, exterior_points
            

###############################################################################################
    #Section references this https://bsouthga.dev/posts/color-gradients-with-python for code. 

    def linear_gradient(self,start_rgb, finish_rgb, n=10):
        ''' returns a gradient list of (n) colors between
        two hex colors. start_hex and finish_hex
        should be the full six-digit color string,
        inlcuding the number sign ("#FFFFFF") '''
        # # Starting and ending colors in RGB form
        s = start_rgb 
        f = finish_rgb 
        
        # Initilize a list of the output colors with the starting color
        RGB_list = [s]
        # Calcuate a color at each evenly spaced value of t from 1 to n
        for t in range(1, n):
            # Interpolate RGB vector for color at the current value of t
            curr_vector = [
                int(s[j] + (float(t)/(n-1))*(f[j]-s[j]))
                for j in range(0,3)
            ]
            # Add it to our list of output colors
            RGB_list.append(curr_vector)
        return RGB_list
          
    # Value cache
    fact_cache = {}
    def fact(self,n):
        # ''' Memoized factorial function '''
        try:
            return self.fact_cache[n]
        except(KeyError):
            if n == 1 or n == 0 or n == 2:
                result = 1
            else:
                result = n*self.fact(n-1)
                self.fact_cache[n] = result
                return result

    def bernstein(self,t,n,i):
        # ''' Bernstein coefficient '''
        binom = self.fact(n)/float(self.fact(i)*self.fact(n - i))
        return binom*((1-t)**(n-i))*(t**i)

    def bezier_interp(self,t,RGB_list,n):
        ''' Define an interpolation function
            for this specific curve'''
        # List of all summands
        summands = [
            list(map(lambda x: int(self.bernstein(t,n,i)*x), c))
            for i, c in enumerate(RGB_list)
            ]
        # Output color
        out = [0,0,0]
        # Add components of each summand together
        for vector in summands:
            for c in range(3):
                out[c] += vector[c]
        return out

    def bezier_gradient(self,RGB_list, n_out=100):
    # ''' Returns a "bezier gradient" dictionary
    #     using a given list of colors as control
    #     points. Dictionary also contains control
    #     colors/points. '''
        n = len(RGB_list) - 1
        gradient = [
            self.bezier_interp(float(t)/(n_out-1),RGB_list,n)
            for t in range(n_out)
            ]
        
        return gradient
    
    def RGB_to_hex(RGB):
        ''' [255,255,255] -> "#FFFFFF" '''
        # Components need to be integers for hex to make sense
        RGB = [int(x) for x in RGB]
        return "#"+"".join(["0{0:x}".format(v) if v < 16 else
                    "{0:x}".format(v) for v in RGB])
    
    def hex_to_RGB(self,hex):
        ''' "#FFFFFF" -> [255,255,255] '''
        # Pass 16 to the integer function for change of base
        return [int(hex[i:i+2], 16) for i in range(1,6,2)]
          
    def polylinear_gradient(self,colors, n):
        ''' returns a list of colors forming linear gradients between
        all sequential pairs of colors. "n" specifies the total
        number of desired output colors '''
        # The number of colors per individual linear gradient
        n_out = int(float(n) / (len(colors) - 1))
        gradients_out = []
        for i in range(len(colors) - 1):
            # Create linear gradient between the current pair of colors
            gradient = self.linear_gradient(colors[i], colors[i+1], n_out)
            # print(gradient)
            # Add the linear gradient to the overall list
            gradients_out.extend(gradient)
        return gradients_out  
          
    def export_conversion_pc(self,file_name):
        try:  
            #TODO
            if (".laz" in file_name or ".las" in file_name):
                hdr = lp.LasHeader(point_format=7, version="1.4")  
                # Set the header information
                
                hdr.scale = [0.001, 0.001, 0.001]  # Scale factors for XYZ coordinates
                hdr.offset = [0.0, 0.0, 0.0]       # Offset for XYZ coordinates
                hdr.data_format_id = 1             # Point format (e.g., 1 for XYZ)
                las_file =  lp.create(point_format=hdr.point_format, file_version=hdr.version)  #lp.LasData(las.header)

                points = np.asarray(self.pointcloud.points)
                col = np.asarray(self.pointcloud.colors)
                # Convert and add points from Open3D point cloud
                las_file.x = points[:, 0]
                las_file.y = points[:, 1]
                las_file.z = points[:, 2]
                las_file.red = (col[:, 0] * 255).astype(int) #col[:, 0]
                las_file.green = (col[:, 1] * 255).astype(int)
                las_file.blue = (col[:, 2] * 255).astype(int)

                # Save the LAS file
                las_file.write(file_name)     
            else:     
                out_cloud = self.pointcloud      
                open3d.io.write_point_cloud(file_name,out_cloud,write_ascii=True)
        except Exception as e:
            print(e)
            print("Error exporting point cloud")
            return "Error exporting point cloud"
          
    #Function to export one single point cloud
    def export_point_cloud(self,file_name):
        try:   
            out_cloud = open3d.geometry.PointCloud()
            out_cloud.translate(np.array([0,0,0]), False)
            for cloud in self.cropped_clouds:
                out_cloud += cloud
                
            if (".laz" in file_name or ".las" in file_name):
                hdr = lp.LasHeader(point_format=7, version="1.4")  
                # Set the header information
                
                hdr.scale = [0.001, 0.001, 0.001]  # Scale factors for XYZ coordinates
                hdr.offset = [0.0, 0.0, 0.0]       # Offset for XYZ coordinates
                hdr.data_format_id = 1             # Point format (e.g., 1 for XYZ)
                las_file =  lp.create(point_format=hdr.point_format, file_version=hdr.version)  #lp.LasData(las.header)

                points = np.asarray(out_cloud.points)
                col = np.asarray(out_cloud.colors)
                # Convert and add points from Open3D point cloud
                las_file.x = points[:, 0]
                las_file.y = points[:, 1]
                las_file.z = points[:, 2]
                las_file.red = (col[:, 0] * 255).astype(int) #col[:, 0]
                las_file.green = (col[:, 1] * 255).astype(int)
                las_file.blue = (col[:, 2] * 255).astype(int)

                # Save the LAS file
                las_file.write(file_name)    
                # las_file = lp.LasData()
                # # Set the header information
                # las_file.header.scale = [0.001, 0.001, 0.001]  # Scale factors for XYZ coordinates
                # las_file.header.offset = [0.0, 0.0, 0.0]       # Offset for XYZ coordinates
                # las_file.header.data_format_id = 1             # Point format (e.g., 1 for XYZ)

                # # Convert and add points from Open3D point cloud
                # for point in out_cloud.points:
                #     x, y, z = point[:3]  # Extract XYZ coordinates
                #     r, g, b = (point[3:6] * 255).astype(int)  # Extract RGB colors and convert to 8-bit

                #     # Add point to LAS file with XYZRGB information
                #     las_file.add_point(x=x, y=y, z=z, red=r, green=g, blue=b)

                # # Save the LAS file
                # las_file.save(file_name)     
            else:   
                open3d.io.write_point_cloud(file_name,out_cloud,write_ascii=True)

        except Exception as e:
            print(e)
            print("Error exporting point cloud")
            return "Error exporting point cloud"
    
    #For exporting multiple clouds at once
    def export_point_clouds(self,file_name, extension):
        try:
            for cloud in range(0,len(self.cropped_clouds)):
                open3d.io.write_point_cloud(file_name + "_" + str(cloud) +"_"+ extension
                                            ,self.cropped_clouds[cloud])
        except Exception as e:
            print(e)
            print("Error exporting point clouds")
            return "Error exporting point clouds"

###############################################################################################
    ###Utility functions###
    
    #Function to load the point cloud
    def load_point_cloud(self,file_path):
        # line = file_path.split("/")
        # name = line[len(line)-1]
        # extension = name.split(".")[1]
        # pointcloud_extensions = ["*.pts","*.ply","*.pcd"]
        
        # # if ".pts" not in file_path:
        # if (extension not in pointcloud_extensions):
        #     print("Error: File is not a valid file")
        #     return "Error: File is not a valid file"
            # return False
            
        try :
            
            if (".laz" in file_path or ".las" in file_path):
                point_cloud = lp.read(file_path)  #lp.file.File(file_path, mode="r")
                points = np.vstack((point_cloud.x, point_cloud.y, point_cloud.z)).transpose()
                colors = np.vstack((point_cloud.red, point_cloud.green, point_cloud.blue)).transpose()
                pcd = open3d.geometry.PointCloud()
                pcd.points = open3d.utility.Vector3dVector(points)
                pcd.colors = open3d.utility.Vector3dVector(colors / 65535)
                self.pointcloud = pcd
            else:
                self.pointcloud = open3d.io.read_point_cloud(file_path)
                if(not self.pointcloud.has_points()):
                    self.status_runnable[0] = False
                    return "Error loading point cloud (Possibly a PTS exported from Recap)"
            #Disable since we are using open3d. 
            # tempFile = open(file_path)
            # self.pointcloudRaw = tempFile.read()
            # tempFile.close()
            # print(self.pointcloudRaw)
            # open3d.visualization.draw_geometries([self.labelCloudFile])
        #Safely catch the error
        except Exception as e:
            print(e)
            print("Error loading point cloud")
            self.status_runnable[0] = False
            return "Error loading point cloud"
        
        
        self.status_runnable[0] = True
        return "Point cloud loaded successfully."

    #This handles the loading of labelCloud data
    def load_labelCloud(self,file_path):
        if ".json" not in file_path:
            print("Error: File is not a .json file")
            return False
        try :
            fjsonObj = open(file_path)
            # self.labelCloudFile = json.load(fjsonObj)
            
            for i in json.load(fjsonObj)['objects']:
                self.labelCloudFile.append(i)
                # print(i)
            fjsonObj.close()
    #Safely catch the error
        except Exception as e:
            print(e)
            print("Error loading label cloud")
            self.status_runnable[1] = False
            return "Error loading label cloud"
        self.status_runnable[1] = True
        return "Labelcloud file loaded successfully."
    
    #This handles the data for the RGB Data
    def load_rgbCloud(self,file_path):
        if ".txt" not in file_path:
            print("Error: File is not a .txt file")
            return False
        try:
            with open(file_path) as rgbTxt:
                lines = rgbTxt.readlines()
                 
                #Append the file to the array with the rgb data
                for line in lines:
                    lineIn = line.replace("\n","")
                    # print(lineIn)
                    if lineIn[0][0] != "!":
                        #Break up the line into the rgb values and the flag at the end. 
                        dat = lineIn.split(" ")

                        #RGB List, then Flag for Inactive or Active
                        self.rgbCloudFile[dat[0].lower()] = [[dat[1],dat[2],dat[3]],[dat[4]]]
            rgbTxt.close()
        except Exception as e:
            print(e)
            print("Error loading rgb cloud")
            self.status_runnable[2] = False #Soft lock to try to load the file
            return "Error loading rgb cloud"
        self.status_runnable[2] = True
        return "RGB file loaded successfully."

    #Check and load all data from the files. Obsolete.
    def getFiles(self, pcFile, lcFile,rgbFile):
        if self.load_point_cloud(pcFile):
            if self.load_labelCloud(lcFile):
                if self.load_rgbCloud(rgbFile):
                    return True, "Files Loaded"
                else:
                    return False, "Error loading rgb cloud"
            else :
                return False, "Error loading label cloud"
        else:
            return False, "Error loading point cloud"
        
    def create_bounding_box(self,center,rotation,extent):
        return open3d.geometry.OrientedBoundingBox(center,rotation,extent)
        
    def setFileNames(self,pcFile,lcFile,rgbFile):
        self.pcFileIn = pcFile
        self.lcFileIn = lcFile
        self.rgbFileIn = rgbFile
        
        boolStat, status = self.getFiles(self.pcFileIn,self.lcFileIn,self.rgbFileIn)
        
        return status
        
    #For use in the recolor by range function. 
    def set_color_1(self,color):
        self.rgbColor1 = color
        self.gradient_colors = self.linear_gradient(self.rgbColor1,self.rgbColor2,n=25)
        
    def set_color_2(self,color):
        self.rgbColor2 = color
        self.gradient_colors = self.linear_gradient(self.rgbColor1,self.rgbColor2,n=25)

    def set_color_3(self,color):
        self.center_median = color
        self.using_target_median = True
        
    #Type sets which list is going to be filled. 
    def set_list_hex_colors(self,colors,type):
        # colors = list_hex_colors.split(" ")
        # RGB vectors for each color, use as control points
        RGB_list = [self.hex_to_RGB(color) for color in colors]
        # self.rgb_colors = RGB_list
        if (type == "replacement"):
            self.replacement_colors = RGB_list
        else:
            self.deletion_colors = RGB_list
        
    def set_list_rgb_colors(self,colors):
        # colors = list_rgb_colors.split(" ")
        #1,2,3 4,3,3 54,6,6
        col_list = []
        for col in colors:
            listTemp = col.split(",")
            for i in range(0,len(listTemp)):
                listTemp[i] = int(listTemp[i])
            col_list.append(listTemp)
        # self.rgb_colors = col_list
        if (type == "replacement"):
            self.replacement_colors = col_list
        else:
            self.deletion_colors = col_list

    def set_coloring_mode(self,mode):
        self.recoloring_mode = mode

    def set_interval(self,intervals):
        self.interval_colors = intervals

    def toggle_threshold_recoloring(self,bool):
        self.spherical_bounding = bool
        
    def toggle_gray_deletion(self,bool):
        self.gray_deletion = bool
###############################################################################################
###############################################################################################
###############################################################################################
class Utils:
    def __init__(self):
        pass
    
    #Advanced Functions for a future me. 
    #Should take in a point with its respective details and return them back to the 
    def recolor_point(point,color):
        print("Function not implemented!")
        pass

    ##Core functions for the pointcloud manipulation  
    def point_is_in_box(self,point,box):
        print("Function not implemented!")
        pass
    
    def calculate_dist_colors(self,color,color_pts):
        #Distances between two different points
        # print(color_pts)
        # print(color)
        d = scipy.spatial.distance.cdist([color],color_pts)
        #Checks if there is a value in the gradient that exceeds the threshold
        for i in d[0]:
            if i > self.color_threshold:
                return True
        return False



    def calc_center(self,pointcloud):
        #Calculate the center of the point cloud
        p = pointcloud.points
        # center = tuple(np.sum(p[:][i]) / len(p) for i in range(3))
        center = tuple([0,0,0])
        
        
        # print(np.sum(p[:][0]))
        # print(center)
        # center = np.mean(pointcloud.points,axis=0)
        return center