import logging
import numpy as np


def random_image(*arg) :
    print "Calling random image func"
    return np.random.random_integers(0.0,1023.0,(1024,1024))


class epics_camera :

    
    def __init__(self, camerapv) :

        
        # Set up logger
        self.__logger = logging.getLogger(__name__)

        # Set up camera PVs 
        self.__basepv = camerapv

        # Get row and columns, bit-depth, and model
        # Using caget as we only need these values once
        self.__nrow = 1024
        self.__ncol = 1024
        self.__nbit = 12
        self.__model = "SIMULATOR"
        self.__naverage = 1

        # Print out status
        print self.__basepv,self.__model
        print self.__nrow,"by",self.__ncol,"@",self.__nbit

        # Set default image function
        self.__imagefunc = random_image


    def set_imagefunc(self,imagefunc) :
        print "New imagefunc set"
        self.__imagefunc = imagefunc

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



    # Set up variable to point to function that will generate image
    def image(self,*arg) :
        return self.__imagefunc(arg)


    def avg_image(self,naverage=None,*arg) :
        return self.image(arg)

    
    def h_projection_avg(self,*arg) :

        self.__logger.debug("Averaged Horizontal Projection")
        hproj = np.sum(self.image(arg),axis=1)                              
        self.__logger.debug("Horizontal Projection Size: %d"%hproj.size)

        return hproj


    def collect_images(self, nimages, *arg):

        # Create an empty 3D numpy array that will store all the images
        allimages = np.empty([nimages, self.__nrow, self.__ncol])

        # Now collect images, use live image threading event to signal
        # when a new image is available
        for index in range(nimages) :
        
            # Add new image to image store
            allimages[index,:,:] = self.image(arg)
           
        return allimages


    def collect_h_projections(self,nprojections,*arg):
        
        self.__logger.info("Collecting %d horizontal projections"%nprojections)
    
        # Create an empty 2D numpy array that will store all the
        # projections - the projections are always 1024 long - fixed
        # by the UNIXCAM IOC.         
        allprojections = np.empty([nprojections, 1024])

        # Collect the projections, using the projectiosn image
        # threading event to signal when a new projection is
        # available. 
        for index in range(nprojections) :
            allprojections[index,:] = np.sum(self.image(arg),axis=1)    


        return allprojections



    



    
if __name__ == "__main__" :

    import time
    import numpy as np
    from utils import GaussFit

    
    logging.basicConfig(level=logging.INFO)
    #logging.basicConfig(level=logging.DEBUG)
        
    cam = epics_camera("SXR:EXS:CVV:01")


    def image(*arg) :
        print "calling custom image func"
        print len(arg),arg

        ncol = 0
        nrow = 0

        if len(arg) == 2 :
            ncol = arg[0]
            nrow = arg[1]

        elif len(arg[0]) == 2 :
            ncol = arg[0][0]
            nrow = arg[0][1]

        elif len(arg[0][0]) == 2:
            ncol = arg[0][0][0]
            nrow = arg[0][0][1]
        


            
#        ncol = arg[0][0][0]
#        nrow = arg[0][0][1]

        gauss_data = GaussFit.gauss(np.arange(ncol),
                                    ncol/2.0,ncol/10.0,
                                    100.0,10.0)
        return np.tile(gauss_data, (nrow,1))
        

            

    cam.set_imagefunc(image)
    
    time_start = time.time()
    print "Collecting images"
    image_store = cam.collect_images(10,cam.ncol,cam.nrow)
    time_diff = time.time() - time_start
    rate = 10.0 / time_diff 
    print "time taken for 10 images:",time_diff," (%f Hz)"%(rate)
    
    
    time_start = time.time()
    print "Collecting images"
    image_store = cam.collect_images(10,cam.ncol,cam.nrow)
    time_diff = time.time() - time_start
    rate = 10.0 / time_diff 
    print "time taken for 10 images:",time_diff," (%f Hz)"%(rate)
    

    time_start = time.time()
    print "Collecting horizontal projections"
    projection_store = cam.collect_h_projections(10,cam.ncol,cam.nrow)
    time_diff = time.time()- time_start
    rate = 10.0 / time_diff 
    print "time taken for 10 projections:",time_diff," (%f Hz)"%(rate)
    
    
    print "Getting averaged images"
    print "Number of averaged images:",cam.get_naverage()
    print "The current image:\n",cam.image(cam.ncol,cam.nrow)
    
    


    print "Getting the average image"
    time_start = time.time()
    print cam.avg_image(cam.ncol,cam.nrow)
    time_diff = time.time()- time_start
    rate = cam.get_naverage() / time_diff     
    print "time taken for",cam.get_naverage(),"averaged images",time_diff,\
        " (%f Hz)"%(rate)
    

    
    cam.set_naverage(240)
    print "Getting 240 average images"
    print cam.get_naverage()
    time_start = time.time()
    print cam.avg_image(cam.ncol,cam.nrow)
    time_diff = time.time()- time_start
    rate = cam.get_naverage() / time_diff     
    print "time taken for 240 averaged images time_diff",time_diff,\
        "(%0.2f Hz)"%(rate)
    
        
    cam.disconnect()
