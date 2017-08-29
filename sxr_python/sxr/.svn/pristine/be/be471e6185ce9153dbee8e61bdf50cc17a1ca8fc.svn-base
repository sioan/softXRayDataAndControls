import logging
import numpy as np

import psana


class daq_camera :

    
    def __init__(self, camera_alias,source="shmem=psana.0:stop=no") :
        
        # Set up logger
        self.__logger = logging.getLogger(__name__)

        # Set up camera PVs 
        self.__name = camera_alias

        self.__logger.debug("Connecting to %s"%self.__name)

        # Get row and columns, bit-depth, and model
        # Using caget as we only need these values once
        self.__nrow = 1024
        self.__ncol = 1024
        self.__nbit = 12
        self.__model = "DAQ"
        self.__naverage = 1

        # Print out status
        print self.__name,self.__model
        print self.__nrow,"by",self.__ncol,"@",self.__nbit

        # Connect to camera
        self.__ds = psana.DataSource(source)
        self.__cam = psana.Detector(self.__name,self.__ds.env())

        # Connect to events
        self.__evtiter = self.__ds.events()


    def disconnect(self) :
        # Does nothing now
        pass


    def set_naverage(self,nimage):
        self.__naverage = nimage

    def get_naverage(self) :
        return self.__naverage

        
    # Define properties to return camera model and image size
    @property
    def nrow(self):
        return self.__nrow

    @property
    def ncol(self):
        return self.__ncol

    @property
    def nbit(self):
        return self.__nbit

    @property
    def model(self):
        return self.__model



    # Get image
    def image(self) :
        self.__logger.debug("Getting image")
        evt = self.__evtiter.next()
        image = self.__cam.raw_data(evt)
        
        if image is None:
            self.__logger.warn("No image found")
                                     
        return image


    def avg_image(self,naverage=None) :
        if naverage is not None :
            self.set_naverage(naverage)

        # create empty array
        self.__logger.debug("Getting averaged image")
        image = np.zeros((self.nrow,self.ncol))

        for i in range(self.get_naverage()) :
            self.__logger.debug("Getting image %d of %d"%(i,
                                                          self.get_naverage()))
            evt = self.__evtiter.next()
            try:
                image += self.__cam.raw_data(evt)
            except:
                self.__logger.error("No data for image %d"%i)

        image /= float(self.get_naverage())

        return image



    
    def h_projection_avg(self,naverage=None) :
        if naverage is not None :
            self.set_naverage(naverage)
            
        self.__logger.debug("Averaged Horizontal Projection")
        hproj = np.sum(self.avg_image(self.get_naverage()) ,axis=1)
        self.__logger.debug("Horizontal Projection Size: %d"%hproj.size)

        return hproj


    def collect_images(self, nimages):
        self.__logger.debug("Collecting %d images"%nimages)
        
        # Create an empty 3D numpy array that will store all the images
        allimages = np.empty([nimages, self.nrow, self.ncol])

        # Now collect images, use live image threading event to signal
        # when a new image is available
        for index in range(nimages) :
            self.__logger.debug("Collected image %d of %d"%(index,nimages))
        
            # Add new image to image store
            allimages[index,:,:] = self.image()
           
        return allimages


    def collect_h_projections(self,nprojections):
        self.__logger.info("Collecting %d horizontal projections"%nprojections)
    
        # Create an empty 2D numpy array that will store all the
        # projections 
        allprojections = np.empty([nprojections, self.ncol])

        # Collect the projections, using the projectiosn image
        # threading event to signal when a new projection is
        # available. 
        for index in range(nprojections) :
            self.__logger.debug("Collected projection %d of %d"%(index,
                                                                 nprojections))
            try:
                allprojections[index,:] = np.sum(self.image(),axis=1)    
            except :
                self.__logger.error("No projection for image %d"%index)


        return allprojections



    



    
if __name__ == "__main__" :

    import time
    import numpy as np
    
    
    #logging.basicConfig(level=logging.INFO)
    logging.basicConfig(level=logging.DEBUG)
        
    cam = daq_camera("TSS_OPAL")

    
    time_start = time.time()
    print "Collecting images"
    image_store = cam.collect_images(10)
    time_diff = time.time() - time_start
    rate = 10.0 / time_diff 
    print "time taken for 10 images:",time_diff," (%f Hz)"%(rate)
    
    
    time_start = time.time()
    print "Collecting images"
    image_store = cam.collect_images(10)
    time_diff = time.time() - time_start
    rate = 10.0 / time_diff 
    print "time taken for 10 images:",time_diff," (%f Hz)"%(rate)
    

    time_start = time.time()
    print "Collecting horizontal projections"
    projection_store = cam.collect_h_projections(10)
    time_diff = time.time()- time_start
    rate = 10.0 / time_diff 
    print "time taken for 10 projections:",time_diff," (%f Hz)"%(rate)
    
    
    print "Getting averaged images"
    print "Number of averaged images:",cam.get_naverage()
    print "The current image:\n",cam.image()
    
    


    print "Getting the average image"
    time_start = time.time()
    print cam.avg_image(10)
    time_diff = time.time()- time_start
    rate = cam.get_naverage() / time_diff     
    print "time taken for",cam.get_naverage(),"averaged images",time_diff,\
        " (%f Hz)"%(rate)
    

    
    cam.set_naverage(240)
    print "Getting 240 average images"
    print cam.get_naverage()
    time_start = time.time()
    print cam.avg_image()
    time_diff = time.time()- time_start
    rate = cam.get_naverage() / time_diff     
    print "time taken for 240 averaged images time_diff",time_diff,\
        "(%0.2f Hz)"%(rate)
    
        
    cam.disconnect()
