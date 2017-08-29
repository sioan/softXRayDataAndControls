import numpy as np
#from scipy.interpolate import spline
import string
#import scipy.optimize as spo
import scipy.io as spio
import matplotlib.pyplot as plt
from pylab import *
import scipy as sp
import math

marker = ['bo-','ro-','go-','mo-']

def APS_data():
	q = [0.0209, 0.025564, 0.030646, 0.035795, 0.0409, 0.04617, 0.05136,0.056559, 0.061753, ]
	tau = [1349, 954, 815, 748, 777, 829, 827, 643, 483] 
	return q,tau
def signum(n):
 if(n < 0): return -1;
 elif(n > 0): return 1;
 else: return n;

class time_stamp_diagnostic:
	def __init__ (self):
	    self.ts_sec = []
	    self.ts_ns = []
	def add(self,sec,ns):
	    self.ts_sec.append(sec)
	    self.ts_ns.append(ns)
	def calc_diff(self):
		 #print self.ts_sec
		 #print self.ts_ns
		 #print np.array(self.ts_ns)*1.0E-9
		 #print np.array(self.ts_sec)
		 time_stamps = np.add(np.array(self.ts_sec),np.array(self.ts_ns)*1.0E-9)
		 time_stamps -= time_stamps[0]
		 self.time_stamps = time_stamps
		 self.time_stamps_diff = np.diff(time_stamps)
		 self.mean = np.mean(self.time_stamps_diff)
		 self.max = np.max(self.time_stamps_diff)
		 self.min = np.min(self.time_stamps_diff)
	def get_diff(self):
	     if not hasattr(self, 'time_stamps_diff'):
                return -1
	     return self.time_stamps_diff
	def get_mean(self):
	     if not hasattr(self, 'time_stamps_diff'):
		self.calc_diff()
	     return self.mean
	def get_time_stamps(self):
             if not hasattr(self, 'time_stamps_diff'):
                return -1
	     return self.time_stamps
	def get_max_min(self):
             if not hasattr(self, 'time_stamps_diff'):
		return -1
	     return self.max, self.min
        def dump_to_file(self, jobName):
	     fina = jobName + "_time_stamps.txt"
	     f_id = file(fina, 'w')
	     f_id.write('# Job name: ' + jobName + '\n')
             f_id.write('# Mean frame spacing = ' + str(self.get_mean()) + '\n')
             header = " # s     ns \n "
             f_id.write(header)
 	     s = np.array(self.ts_sec, ndmin =2)
 	     ns = np.array(self.ts_ns, ndmin =2)
	    # print s.shape
             temp = np.concatenate((s,ns), axis = 0)
	    # print np.transpose(temp)
	      #temp = np.reshape(temp, (len(temp)/2,2))
             np.savetxt(f_id, np.transpose(temp), fmt='%-20d')
	     f_id.close()
	def load_from_file(self, fina):
	     pass
       	     f_id = file(fina,'r')
             header = []
	     for i in range(3):
	         header.append(f_id.readline())
	     data = np.loadtxt(f_id)
	     self.ts_sec = data[:,0]
	     self.ts_ns = data[:,1]
	     f_id.close()
	     #print self.ts_sec
	     #print self.ts_ns
	def plot (self, fig_no = 1):
	     if not hasattr(self, 'time_stamps_diff'):
	     	self.calc_diff()
	     
	     
	     plt.figure(fig_no)
	     plt.subplots_adjust(hspace=.5)
	     plt.subplot(211)	
	     plt.title("Time stamp difference ")	
	     plt.plot(self.time_stamps_diff)
	     plt.xlabel("Time [s] ")
	     plt.ylabel(r"$\Delta t$")
	     plt.subplot(212)
	     plt.title("Histogram")
	     plt.ylabel("# samples ")
	     plt.xlabel(r"$\Delta t$")
	     plt.hist(self.time_stamps_diff)


def correlator(x,y, LLD = 0):
	v = len(x)
	out = np.zeros((v-1,1))
	IP = np.zeros_like(out)
	IF = np.zeros_like(out)
	counter = np.zeros((v-1,1))
	for tau in range(1,v+1):
		for i in range(0,v-tau):
			#print "tau = ",tau
			#print "i = ",i
			#print out
			#print counter
			#print [tau - 1,1]
			if (x[i]>LLD)and(y[i+tau]>LLD):
			    out[tau - 1,0] += x[i]*y[i+tau]
			    counter[tau - 1,0] += 1
			    IP[tau-1,0] += x[i]
			    IF[tau-1,0] += y[i+tau] 
			    np.ad
			#print "out = ",out
			#print "counter = ",counter
	out = np.divide(out[:,0],counter[:,0])
	IP = np.divide(IP[:,0],counter[:,0])
	IF = np.divide(IF[:,0],counter[:,0])
	den = np.multiply(IP,IF)
	out = np.divide(out,den)
	return np.arange(1,v),out
def generate_tau(n, step = 10):
	tau = np.zeros((1,n),np.int32)
	counter = 0;
	for i in range(1,10):
		for j in range(0,10):
		#	print counter,i,j
			tau[0,counter] = (j+1**(i-1))**i
			if tau[0,counter] > tau[0,counter-1]: 
			    counter +=1
			if (counter == n):
		#		print "tau = ",tau
				return tau

def avg_img(n,frame, frames_per_interval, avg_img,counter):
	interval = np.ceil(n / frames_per_interval);
	avg_img[interval-1] += frame
	counter[interval-1] += 1;
	return avg_img, counter	
def calculate_SAXS(smask,qs, avg_img):
	saxs = np.zeros((len(qs),1))
	print "size of mask = ", np.array(smask).shape
	for i in range(0,len(qs)):
		saxs[i] =  np.mean(avg_img[smask[i][0],smask[i][1]])
		print saxs[i]
	return saxs
def plot_SAXS(qs,saxs, fig_no = 1,job_name = '', frames_per_interval = 0 ):
	m1 = 1e9
	m2 = 0 
	number_of_plots = saxs.shape[1]
	plt.figure(fig_no)
	#plt.loglog(qs,saxs,'ko-')
	
	plt.title("S(q)", size = 'xx-large')	
	for i in range(0,number_of_plots):
		t1 = np.min(saxs[:,i])
		if t1< m1:
			m1 = t1;
		t1 = np.max(saxs[:,i])
		if t1 > m2:
			m2 = t1;
		#plt.loglog(qs,saxs[:,i], marker[i])
		if i == 0:
			plt.hold(True)
	if number_of_plots >1:
		avg_saxs = np.mean(saxs,axis = 1)
		plt.loglog(qs,avg_saxs,'k-')
	plt.xlabel('q [nm$^{-1}$]', size = 'x-large')
	plt.xlim([np.min(qs),np.max(qs)])
	plt.ylabel('Int. [arb. units]', size = 'x-large')
	plt.ylim([0.6*m1,2*m2])
	plt.hold(False)

def blemish(det):
	if det == "TimePix":
		print "blemish"
		blemish = np.ones((512,512),np.int8)
		blemish[255:258,:] = 0
		blemish[:,255:258] = 0
		blemish[0:2,:] = 0
		blemish[:,0:2] = 0
		blemish[510:,:] = 0
		blemish[:,510:] = 0
	elif det == "PI":
		blemish = np.ones((1300,1340),np.int8)
	return blemish	

def map_image(s,beam0, pixel_size, sample_detector,energy,det_pos,sense = [1,1],phi = False):
	q_map = np.zeros(s,np.float32)
	wavelength = 1.236/energy
#	print "tools = ", beam0, s
	# direct beam      
        xDBpix = beam0[0] + sense[0]*(det_pos[1][0] - det_pos[0][0]) / pixel_size[0]
        yDBpix = beam0[1] + sense[1]*(det_pos[1][1] - det_pos[0][1]) / pixel_size[1]
	#print xDBpix, yDBpix
	pre = 4*(math.pi/wavelength)
	for i in range(0,s[0]):
		for j in range(0, s[1]):
			 R = sqrt((pixel_size[0]**2)*(yDBpix-i)**2 + (pixel_size[1]**2)*(xDBpix-j)**2)
			# print R, R/sample_detector
			 #print 0.5*np.arctan(R/sample_detector)
			 #print  np.sin(0.5*np.arctan(R/sample_detector))
			 #print pre* np.sin(0.5*np.arctan(R/sample_detector))
			 #raw_input()
			 q_map[i,j] = np.sin(0.5*np.arctan(R/sample_detector));
	
	q_map = q_map*pre
	#print pre, wavelength
	#plt.figure(4)
	#plt.imshow(q_map)
	#plt.colorbar()
	#plt.show()
	return q_map
	




def map_image_refl(s,alpha,beam0,beam_s,pixel_size, sample_detector,energy,det_pos, sense = [1,1]):
	# input parameters:
		#  s: frame size
		#  alpha: incident angle in [rad] 
		#  beam0: direct beam position ([x0,y0])
		#  pixel_size
		#  sample_detector: sample to detector distance
		#  energy:  energy of x-rays [keV]
	        #  det_pos: 3x2 array of detector postion during direct beam measurements, specular beam measurements, spekcle pattern collection
        # Output: who knows what really is going to come out :)
        
     #print  det_pos[0][0], det_pos[0][1]
     #print det_pos[1][0], det_pos[1][1]
     #print det_pos[2][0], det_pos[2][1]
     #print beam0
     #print beam_s
        
        
     alpha = (math.pi/180.0)*alpha
     q_map = np.zeros(s,np.float64)
     wavelength = (1.236)/energy  #   [nm] are desired units 
     xmm = np.zeros(s,np.float64)
     ymm = np.zeros(s,np.float64)
     d2Beam0 = np.zeros(s,np.float64)
  
     # direct beam	
     xDBpix = beam0[0] + sense[0]*(det_pos[2][0] - det_pos[0][0]) / pixel_size[0]
     yDBpix = beam0[1] + sense[1]*(det_pos[2][1] - det_pos[0][1]) / pixel_size[1]	
     # specular beam
     xRBpix = beam_s[0] + sense[0]*(det_pos[2][0] - det_pos[1][0]) / pixel_size[0]
     yRBpix = beam_s[1] + sense[1]*(det_pos[2][1] - det_pos[1][1]) / pixel_size[1]
     for i in range(s[0]):
        for j in range(s[1]):
           xmm[i,j] = j - xDBpix
           ymm[i,j] = i - yDBpix
     d2Beam0 = np.sqrt(np.add((pixel_size[0]**2)*xmm**2,(pixel_size[1]**2)*ymm**2))	
     # distance from the direct beam to the reflected beam [mm]
     xDB2RB = (xRBpix - xDBpix) * pixel_size[0]                                    
     yDB2RB = (yRBpix - yDBpix) * pixel_size[1]
     dDB2RB = sqrt( xDB2RB**2 + yDB2RB**2)	
     #print xDBpix, yDBpix,  xRBpix , yRBpix, dDB2RB
     # calculate the true incident angle for the measurement of the specular
     dDB2RB = sqrt( xDB2RB**2 + yDB2RB**2)	                                   
     true_alpha = 0.5*math.atan( dDB2RB / sample_detector)
     alpha= true_alpha
     print "true_alpha = ",true_alpha 	
     # determine the tilt angle of the streak with respect to the
     if ( yDB2RB != 0 ):
        tilt = math.atan( xDB2RB / yDB2RB )                                     
     else:
        tilt = signum(xDB2RB) * math.pi / 2                                       
     # projected distance of each pixel to the Plane Of Reflection [POR])
     # [positive means above the streak, negative below the streak]
     d2POR = np.zeros(s, np.float32)  
     d2POR = xmm* math.sin(math.pi/2 - tilt)	                                             
     v = np.where(ymm != 0)
     d2POR[v] =  np.multiply(d2Beam0[v],np.sin(np.arctan(np.divide(xmm[v],1.0*ymm[v])) - tilt))            
     v = np.where(xmm > 0)
     v2 = np.where(ymm == 0)
     r = [i for i in v if i in v2]
     t = np.ones_like(xmm)
     t[xmm<0]  = 0
     t[ymm!=0]  = 0
     v = np.where(t ==1)  
     d2POR[v] =  d2Beam0[v]* math.sin(-math.pi/2 - tilt)
     v = np.where(xmm < 0)
     v2 = np.where(ymm == 0)
    # r = [i for i in v and i in v2]
     #v = r 
     #print "v = ",v
     #print v2
     t = np.ones_like(xmm)
     t[xmm>0]  = 0
     t[ymm!=0]  = 0		
     v = np.where(t ==1)	
     #raw_input() 	
     d2POR[v] =  d2Beam0[v]* math.sin(math.pi/2 - tilt)
     v = np.where(ymm == 0)
     v2 = np.where(xmm == 0)
     r = [i for i in v if i in v2]
     t = np.ones_like(xmm)
     t[xmm!=0]  = 0
     t[ymm!=0]  = 0
     v = np.where(t ==1)  
     d2POR[v] =  d2Beam0[v]* math.sin(-tilt)
     # in plane exit angle of each pixel (not true exit angle)
     
     inPlaneExitAngle =   np.arctan(np.sqrt(np.subtract((d2Beam0)**2,d2POR**2))/sample_detector)- alpha
    
     # distance of projected point (PPT) to sample
     dPPt2Sample = np.sqrt(np.subtract(d2Beam0**2,d2POR**2)+ sample_detector**2)
    # out of plane angle
     outOfPlaneAngle = np.arctan(np.divide(d2POR,np.multiply(dPPt2Sample,np.cos(inPlaneExitAngle))))   
     # true exit angle
     exitAngle = np.multiply(np.sign(inPlaneExitAngle), np.arccos(np.divide(np.sqrt(np.add(d2POR**2,np.multiply(dPPt2Sample,np.cos(inPlaneExitAngle))**2)), np.sqrt(d2Beam0**2 + sample_detector**2))))
     #exitAngle = inPlaneExitAngle
    
     qz = 2*math.pi/wavelength* np.add(np.sin(alpha), sin(exitAngle))
     qx = 2*math.pi/wavelength * np.subtract( cos(alpha), np.multiply(np.cos(exitAngle),np.cos(outOfPlaneAngle))) 
     qy = 2*math.pi/wavelength * np.multiply( np.cos(exitAngle),np.sin(outOfPlaneAngle))              
     qp   = np.sqrt(qx**2 + qy**2)                 
     #print tilt
     #plt.figure(1)
     #plt.imshow(qp)
     #plt.colorbar()#
     #plt.show()
     return qp    





 
    #q_map = np.zeros((RC[1]-RC[0],RC[3]- RC[2]),np.float16)
    #wavelength = np.float16(1.236/energy)
    #xmm = np.zeros_like(q_map)
    #ymm = np.zeros_like(q_map)
    #for n1 in range(0,RC[1]-RC[0]):
     #   for n2 in range(0,RC[3]-RC[2]):	
        	#R = sqrt((n1- beam0[0])**2 + (n2- beam0[1])**2)
        	#
        	#q_map[n1,n2] = 4*(math.pi/wavelength)*np.sin(0.5*np.arctan( R / sample_detector))
    
#    xpix = np.array(range(0,RC[1]-RC[0]), np.float16)                           
#    ypix = np.array(range(0,RC[3]-RC[2]), np.float16)
#    #print xpix.shape
#    ## xpix, ypix
#    xmm  = np.ones((len(ypix),1),np.float16) * ((beam0[1] - xpix )) * pixel_size[0];
#    ymm  = np.rot90(((beam0[0] )- ypix) * pixel_size[1] * np.ones((len(xpix),1),np.float16));
#    R = np.float16(np.sqrt( xmm**2 + ymm**2));
#    wavelength = np.float16(1.236/energy)
#    q_map =  np.fliplr(np.rot90((4*(math.pi/wavelength)*np.sin(0.5*np.arctan( R / sample_detector))),1))
#    plt.figure()
#    if phi:
#        phi_map = np.arctan2(-ymm,xmm); 
#        phi_map = phi_map + math.pi;
#        return q_map, phi_map
#    else:
#        return q_map
def part( info, fina = "", mat = True):
	part_d = []
	part_s = []
	part_s_list = []
	part_d_list = []
	mask = info['ROI']
	m1 = np.min(info['qmap'][mask>0])
	m2 = np.max(info['qmap'][mask>0])
	# this has to be deleted after test
 	step1 = (m2-m1)
	step2 = step1	
#	step1 = (m2-m1)/(info['ndynamic'].get())
#	step2 = (m2-m1)/(info['nstatic'].get())
	q = info['qmap']
	#print "q_map shape", q.shape, step1, step2,info['ndynamic'].get(),info['nstatic'].get()
	RC = info['RC'] 
	q[q<m1] = m1
	blemish = np.ones((1300,1340))
	part_d_img = np.multiply(np.int8(np.multiply(np.floor_divide(q - m1,step1)+1,mask)), blemish)#(info['detector']['Name'])[RC[0]:RC[1],RC[2]:RC[3]])
	part_s_img = np.multiply(np.int8(np.multiply(np.floor_divide(q - m1,step2)+1,mask)), blemish)#(info['detector']['Name'])[RC[0]:RC[1],RC[2]:RC[3]])
	
        #print part_d_img.shape
	#raw_input()
	temp = np.where( part_d_img == 0)
        part_d.append(temp)
        part_s.append(temp)
	for i in range(1,2):#info['ndynamic'].get()+1):
		temp = np.where( part_d_img < 2000)
		part_d.append(temp)
		part_d_list.append(np.mean(q[temp]))
		
	for i in range(1,2):#info['nstatic'].get()+1):
	#	temp = np.where( part_s_img == i)
		part_s.append(np.where( part_s_img <2000))
		part_s_list.append(np.mean(q[np.where( part_s_img == i)]))
	if len(fina) != 0:
		if mat:
			spio.savemat(fina,{'part_s': part_s, 'part_d': part_d}) 
		np.savez(fina, part_s = part_s, part_d = part_d, part_d_list = part_d_list, part_s_list = part_s_list, mask = mask, RC = info['RC'])
			#det_pos = info['detector_position'], beam0 = info['beam0'], beam_spec = info['beam_spec']) 
	return part_d_img, part_s_img, part_d, part_s, part_d_list, part_s_list

    
def read_parameters(s):
	sources = []
	while 1:
		x = string.find(s,",")
		if (x == -1):
			return sources
		x2 = len(s)
		sources.append(s[0:x])
		s=s[x+1:x2]
		if (x2 == x+1):
			 return sources
	
def gauss(mu, sigma,A,bgnd, x, dim = 1 ):
	if dim == 2:
		return 100*exp(-((( mu[0]-x[0])/sigma[0])**2+((mu[1]-x[1])/sigma[1])**2)/2)
	else:
		return A*(1.0/(sigma*sqrt(2*pi)))*exp(-(x-mu)**2/(2.0*sigma**2)) + bgnd 

def knife_edge_fun(x0,sigma,A,x):
	# in case of troubles, comment lines from A to B
	# A
#	m1 = np.min(x)
#	m2 = np.max(x)
#	if m1*m2 <= 0 :
#		temp = m2
#               x = x + m2
#	elif (m1*m2 > 0 ) and m1 < 0:
#		temp = 0
#                x = -1.0 * x
#	elif (m1*m2 > 0 ) and m1 > 0:
#		temp = 0
	# B
	u = ((x - x0)/sigma)/math.sqrt(2)
	Q = sp.special.erfc(u)
	return A*Q 
	
def gauss_2D(p, x,y):
	h,mux,muy, sigmax,sigmay = p
	# h,mux,sigmax
	return h*exp(-((( mux-x)/sigmax)**2+((muy-y)/sigmay)**2)/2)

def vvv(a,b,c,x):
	pass
def smooth(y, n = 3):
	v = (n-1)/2
	vv = []
	for i in range(v,len(y)-v):
		vv.append(np.mean(y[i-v:i+v]))
	return vv
def sxr_smooth(x,y, n = 3.0):
	y_smooth = np.zeros((np.floor(len(y)/n)))
        x_smooth = np.zeros((np.floor(len(y)/n)))

	#print len(y)
	#print len(y_smooth)
	x = x[0:len(y_smooth)*n]
	y = y[0:len(y_smooth)*n]
	#print y
	#print y[0::n]
	#y_smooth = np.zeros((1,np.floor(len(y)/n)))
	#x_smooth = np.zeros((1,np.floor(len(y)/n)))
	for b2 in range(n):
	 #  print b2
          # print y[b2::n]
	   
           np.add(y_smooth, y[b2::n],y_smooth)
	   np.add(x_smooth, x[b2::n],x_smooth)
	n = n*1.0
	#print x_smooth/n, y_smooth
	return x_smooth/n, y_smooth/n
	
def knife_edge_scan(x_data,y_data,algorithm = [1,1], fig_no = 1):
	#m = np.min(x_data)
	x_data = np.array(x_data)
	y_data = np.array(y_data)
	x_data.ravel()
	y_data.ravel()
	plt.figure(fig_no)
        plt.subplot(121)
        plt.plot(x_data,y_data,'ko')
	m = np.min(x_data)
        x_data += abs(m)

	if algorithm[0] == 1:
		fitfunc = lambda p,x_data: knife_edge_fun(p[0],p[1],p[2],x_data)
		#p0 = [0.7*np.mean(x_data),np.mean(x_data)/10, 1]
		p0 = [0.7*np.max(y_data),np.max(y_data)/10, 1]
		out = fit_1D(x_data,y_data,fitfunc,p0)
		#print out
	        p1 = out[0]
		#print p1
	        #raw_input() 
		p1[0] += m 
        	pcov = out[1]
	        x_data += m

		yhat = fitfunc(p1,x_data)   # get predicted observations
        	SSE = np.sum((y_data-yhat)**2)
        	sig2 = SSE/(len(y_data)-len(p1))
        	ecov = sig2*pcov
		plt.hold(True)
		#x_data += m

       		y_fit = fitfunc(p1,x_data)
		#x_data += m
        	plt.plot(x_data,y_fit,'r')
        	v1 = np.where(y_fit>0.159*np.max(y_fit))
        	v2 = np.where(y_fit>0.81*np.max(y_fit))
                plt.plot(x_data[v1], np.ones_like(x_data[v1])*0.159*np.max(y_fit),'b--')
                plt.plot(x_data[v2], np.ones_like(x_data[v2])*0.841*np.max(y_fit),'b--')
                s = '$x_0$ = % .5f $\pm$ %.5f \nw = % .5f $\pm$ %.5f' % (p1[0],sqrt(ecov[0][0]), p1[1], sqrt(ecov[1][1]))
	       	plt.title(s)
	if algorithm[1] == 1:
#		print y_data[0:-1]
	#	raw_input()
		x_data_smooth, y_data_smooth = sxr_smooth(x_data[0:-1], y_data[0:-1], n = 5)
		plt.subplot(121)
		plt.hold(True)
                plt.plot(x_data_smooth,y_data_smooth,'bo')
                #plt.hold(True)
	#	plt.show()
		print "############################################################################"
		y_data = -1.0*np.divide(np.diff(y_data_smooth),np.diff(x_data_smooth))
		y_data[y_data<0] = 0.0
                x_data = x_data_smooth[0:-1]
#		print len(x_data_smooth), len(y_data_smooth)
#		print len(x_data), len(y_data)
		plt.subplot(122)
		plt.plot(x_data,y_data,'bo')
		plt.hold(True)
	#	sxr_smooth(x_data,y_data)
		#plt.plot(sxr_smooth(x_data,y_data),'ro')
		#plt.show()
	        #plt.plot()
		#y_data = np.divide(np.diff(y_data_smooth),np.diff(x_data))
                #x_data = x_data[1::]
                #fitfunc = lambda p,x_data: gauss(p[0],p[1],p[2],p[3],x_data)

		#plt.plot(x_data, y_data,'ko')
		#plt.hold(True)
		#print len(y_data_smooth), len(x_data)
		#plt.plot(x_data[(n-1)/2-1:len(y_data)-(n-1)/2-1],y_data_smooth,'b')
		#x_data = x_data[(n-1)/2-1:len(y_data)-(n-1)/2-1]
		#y_data = np.divide(np.diff(y_data_smooth),np.diff(x_data))
		#x_data = x_data[1::]
		fitfunc = lambda p,x_data: gauss(p[0],p[1],p[2],p[3],x_data)
		p0 = moments_1D(x_data,y_data)
  		out = fit_1D(x_data,y_data,fitfunc,p0)
                p1 = out[0]
		#p1[1] *= 2.35482
                pcov = out[1]
                yhat = fitfunc(p1,x_data)   # get predicted observations
                SSE = np.sum((y_data-yhat)**2)
                sig2 = SSE/(len(y_data)-len(p1))
                ecov = sig2*pcov
		s = '$x_0$ = % .2f $\pm$ %.3f \n  FWHM = %.2f $\pm$ %.3f' % (p1[0],sqrt(ecov[0][0]),p1[1]*2.35482,sqrt(ecov[1][1]*2.35482))
 		plt.title(s)
		y_fit = fitfunc(p1,x_data)
                plt.plot(x_data,y_fit,'r')


def make_histogram(data,n_bins,range2,mask):#, saturated):
	
	#mask[saturated == 1] = 0
        x = data[mask].ravel();
        return  np.histogram(x, bins = n_bins, range = range2)
       
       
def bin_image(img,bin_size):
    s = img.shape
    #bin_size = np.array(bin_size)
    r = np.remainder(np.array(s), bin_size)
    # bin_size, r
    if np.sum(r) > 0:
        return -1
    s2 = np.divide(np.array(s), bin_size)
    y = np.zeros((s2))
    for i in range(0,s2[0]):
        for j in range(0,s2[1]):
            a = i*bin_size[0]
            b = j*bin_size[1]
            y[i,j] = np.sum(img[a:a+bin_size[0],b:b+bin_size[1]])
    return y
   
def fit_1D(x_data,y_data,fitfunc,p0):
	#A = np.vstack([x_data, np.ones(len(x_data))]).T
	errfunc = lambda p, x, y: fitfunc(p, x) - y # calculate chi
	return spo.leastsq(errfunc, p0[:], args=(x_data, y_data), full_output = 1 )


def fit_2D(x,y, z, fitfunc, p0):
	#errfunc = lambda p: ravel(gaussian(*p)(*indices(data.shape)) - data
    # p0[:]
    errfunc = lambda p0, x,y, z: np.ravel(fitfunc(p0,x,y) - z) # calculate chi
	#params = [[30,30],[50, 50]
    # x,y,z
    p = spo.leastsq(errfunc, p0, args = (x,y,z))
    return p

def gaussian(height, center_x, center_y, width_x, width_y):
    """Returns a gaussian function with the given parameters"""
    width_x = float(width_x)
    width_y = float(width_y)
    return lambda x,y: height*exp(
                 -(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2)
def moments(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution by calculating its
    moments """
    total = data.sum()
    print "kkk ", data.shape
    X, Y = indices(data.shape)
    x = (X*data).sum()/total
    y = (Y*data).sum()/total
    col = data[:, int(y)]
    width_x = sqrt(abs((arange(col.size)-y)**2*col).sum()/col.sum())
    row = data[int(x), :]
    width_y = sqrt(abs((arange(row.size)-x)**2*row).sum()/row.sum())
    height = data.max()
    return height, x, y, width_x, width_y 
def fitgaussian(data):
     """Returns (height, x, y, width_x, width_y)
     the gaussian parameters of a 2D distribution found by a fit"""
     params = moments(data)
     errorfunction = lambda p: ravel(gaussian(*p)(*indices(data.shape)) - data)
     p, success = spo.leastsq(errorfunction, params)
     return p
def moments_1D(x_data,y_data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution by calculating its
    moments """
    bgnd = np.min(y_data)
    data = y_data - bgnd
    height = data.max()
    total = data.sum()
    data = np.divide(data,total)
    x = (np.multiply(x_data,data)).sum()
    E = np.sum(np.multiply(x_data,data))
    sigma = np.sqrt(np.sum(np.abs(np.multiply(np.power((x_data-E),2),data))))
    return  E, sigma, total, bgnd
	
def speckle_size_x(img, max_delta = 50):
	
	s = np.zeros((img.shape[1]-1))
	d1 = np.zeros_like(s)
	d2 = np.zeros_like(s)
	rows =  img.shape[0]
	if max_delta > img.shape[1]:
		max_delta = img.shape[1]
	for delta_x in range(1,max_delta):
		temp = np.zeros(rows)
		temp_d1 = np.zeros((rows))
		temp_d2 = np.zeros(rows)
		counter = 0 
		for i in range(img.shape[1]-delta_x):
			temp += np.multiply(img[:,i],img[:,i+delta_x])

			#print img[:,i]
			#print img[:,i+delta_x]
			#print (np.add(img[:,i], img[:,i+delta_x])).transpose()/2.0 
			#print (np.add(np.power(img[:,i],2), np.power(img[:,i+delta_x],2))).transpose()/2.0

			np.add(temp_d1, (np.add(img[:,i], img[:,i+delta_x])).transpose()/2.0, temp_d1)
			np.add((np.add(np.power(img[:,i],2), np.power(img[:,i+delta_x],2))).transpose()/2.0,temp_d2, temp_d2) 
			counter += 1
		#	print img[:,i]
		#	print img[:,i+delta_x]
		
			#print "temp = ", temp
			#print "temp_d1 = ", temp_d1
			#print "temp_d2 = ", temp_d2

#			raw_input()
		s[delta_x-1] = np.mean(temp)/counter
		d1[delta_x-1] = np.power(np.mean(temp_d1)/counter,2)
		d2[delta_x-1] = np.mean(temp_d2)/counter
	#	print "s = ", s
	#	print d1
	#	print d2
	return np.divide(np.subtract(s,d1),np.subtract(d2,d1)) 
def speckle_size_y(img, max_delta = 50):

        s = np.zeros((img.shape[0]-1))
        d1 = np.zeros_like(s)
        d2 = np.zeros_like(s)
        cols =  img.shape[1]
        if max_delta > img.shape[0]:
                max_delta = img.shape[0]
        for delta_y in range(1,max_delta):
                temp = np.zeros(cols)
                temp_d1 = np.zeros((cols))
                temp_d2 = np.zeros(cols)
                counter = 0 
                for i in range(img.shape[0]-delta_y):
                        temp += np.multiply(img[i,:],img[i+delta_y,:])

                        #print img[:,i]
                        #print img[:,i+delta_x]
                        #print (np.add(img[:,i], img[:,i+delta_x])).transpose()/2.0 
                        #print (np.add(np.power(img[:,i],2), np.power(img[:,i+delta_x],2))).transpose()/2.0
      
                        np.add(temp_d1, (np.add(img[i,:], img[i+delta_y,:])).transpose()/2.0, temp_d1)
                        np.add((np.add(np.power(img[i,:],2), np.power(img[i+delta_y,:],2))).transpose()/2.0,temp_d2, temp_d2)
                        counter += 1
                #       print img[:,i]
                #       print img[:,i+delta_x]

                        #print "temp = ", temp
                        #print "temp_d1 = ", temp_d1
                        #print "temp_d2 = ", temp_d2
    
#                       raw_input()
                s[delta_y-1] = np.mean(temp)/counter
                d1[delta_y-1] = np.power(np.mean(temp_d1)/counter,2)
                d2[delta_y-1] = np.mean(temp_d2)/counter
        #       print "s = ", s
        #       print d1
        #       print d2
        return np.divide(np.subtract(s,d1),np.subtract(d2,d1))


if __name__== '__main__':
	a = np.zeros((100,100))
	n_speckles = 100
	#print a
	x = ((np.random.rand(n_speckles)-0.5)*(a.shape[0]-5)).astype(np.int)+a.shape[0]/2
	y = ((np.random.rand(n_speckles)-0.5)*(a.shape[1]-5)).astype(np.int)+a.shape[1]/2
	for i in range(n_speckles):
		a[x[i],y[i]] += 1 
		a[x[i],y[i]-1] += 1
		a[x[i],y[i]-2] += 1
		a[x[i],y[i]-3] += 1
		a[x[i],y[i]-4] += 1
		a[x[i],y[i]-5] += 1
                a[x[i]-1,y[i]] += 1
                a[x[i]-2,y[i]] += 1
                a[x[i]-3,y[i]] += 1
                #a[x[i]-4,y[i]] += 1
                #a[x[i]-5,y[i]] += 1
#	print "img = ",a
	#speckle_size(a)
	#raw_input()
#	plt.figure(1)
#	plt.subplot(211)
#	plt.imshow(a)
#	plt.subplot(212)
#	plt.plot(range(1,a.shape[1]),speckle_size_x(a), 'ko-')
#	plt.hold(True)
#	plt.plot(range(1,a.shape[1]),speckle_size_y(a), 'bo-')
#	plt.show()	
#s = (1300,1340)
#	alpha = (math.pi/180)*(0.1)
        #beam0 = [550,50]
#	beam_s = [590,450]
#	pixel_size = [20E3,20E3]
#       sample_detector = 4
#	energy  = 8E9
#	det_pos = [[1,1],[1,1],[5E6,4E6]]
#	sense = [-1,-1]
 #       map_image_refl(s,alpha,beam0,beam_s,pixel_size, sample_detector,energy,det_pos, sense )




	x = np.arange(-200,-10,2.0)
	y =  knife_edge_fun(-100,20,5,x)# +  np.random.rand(x.shape[0])
	#a= np.loadtxt('test_data.txt')
	#x = a[:,1]
	#y = a[:,2]
	y_fit = knife_edge_scan(x,y, algorithm = [ 1,1])
	#plt.figure(1)
	
	
	plt.show()
  #   read_parameters("test,test,1,")
#	fitfunc = lambda p, x:p[2]*(1.0/(p[1]*sqrt(2*pi)))*exp(-(x-p[0])**2/(2.0*p[1]**2))
#	x_data = np.arange(-10,10,1)
#	y_data = 5*gauss(1.5,3,x_data)
#	noise = np.random.normal(0, .06, x_data.shape)
#	p0 = [-1,11,13]
##	p1, success = fit_1D(x_data,y_data,fitfunc,p0)
#	fig = plt.figure(1)
#	img = np.load("e170-r0052-s00-c00_avg_img.npy")
#	y = bin_image(img,[4,4])
##	plt.plot(x_data,y_data + noise,'ro')
##	plt.plot(x_data,fitfunc(p1, x_data), 'b')
##	 success
#	if (np.sum(y) == -1):
#		 "Choose the bin size wisely !!!!!!!!!!!!! "
#	else:
#		plt.subplot(211)
#		plt.imshow(img)
#		plt.subplot(212)
#		plt.imshow(y)
#		plt.show()
#	
#    mask = np.ones((512,512))
#    mask[100:512] = 1
#    q, phi_map = map_image([512,512],[300,300], [55E3,55E3], 4.5E9,7.908, phi = True)
#    #part_d_img, part_s_img,part_d, part_s = part(q,100, 18, mask, fina = "bbbb.npz")
#    temp = np.load("bbbb.npz")
#   #  np.max(part_d_img),np.min(part_d_img)
#    part_s =temp['part_s']
#    part_d =temp['part_d']
#     temp
#     len(part_d[0])
#    Xin, Yin = mgrid[0:401, 0:401]
#    data = gaussian(300., 210., 210., 20., 10.)(Xin, Yin)+  + np.random.random(Xin.shape)
#    params = fitgaussian(data)
#    print moments(data)
#    print "fit1 = ",params
#    fit = gaussian(*params)(Xin, Yin)
#    xy_data = [Xin,Yin]
#    fun = lambda p,x,y: gauss_2D(p,x,y) #p[0],p[1],p[2],p[3],p[4]
#    p0 = moments(data)#[100,10,10,2,30]
#    
##    f2 = fit_2D(Xin, Yin,data, fun, p0)
##    print "fit2 = ", f2[0]
#			
#    x = np.array([[1,1],[1,1]])
#    print x/2.
#    #raw_input("sss")
#    x =np.arange(0,1000)*(6.28/180)
#    x= np.sin(4*x)+1
#    y = [1,1,1,1]
#    m = 2000
#   # x = np.transpose(np.random.randn(m))
#    #x = np.random.gamma(1,3,m)
#    tau = generate_tau(4, step = 10)
##    a,b = correlator(x,x, LLD = 0.3)
##    hh = np.correlate(x,x,'full')
##    print np.transpose(hh)
##
#    fig = plt.figure()
##    plt.subplot(311)
##    #plt.hist(x,200)
##    plt.plot(x)
##    plt.subplot(312)
##    plt.plot(a,b)
##    plt.subplot(313)
##    plt.semilogx(hh[m-1:])
##    #plt.colorbar()
#    t = np.zeros((3,3,2))
#    print "kkkk = ",np.isnan(t)
#    if (np.mean(np.isnan(t)) > 0) :
#    	print('ggg')
#    else:
#    	print('hhh')
#	
#    plt.semilogy(tau[0,:])
#    plt.show()
##
##
##

