from pylab import *
from scipy.signal import medfilt

#1) collect all data into one place. 
#	a) xpptut15 run 360 (i.e. amoe1616 20) has the Cu edge on an andor
#	b) ask alex to get cold andor background noise
#	c) single image hit counts from sxrlp2615 runs 123-125, 127-139, 144-161,164-177
	
#2) generate compared histogram of counts vs I for fourier reduced and non fourier reduced. use xpptut15 run 360
#3) get single image hit counts from sxrlp2615 to show where the oxygen edge is.
#4) generate gaussian shape for single shot filtering. more complicated than anticipated. don't know gaussian specs to 

window_size = 11
#median outlier removal
def outlier_removal(y,window_size):
	#smoothed = convolve(y,ones(window_size)*1.0/window_size,mode="same")
	smoothed = medfilt(y,window_size)
	stan_dev = std(y-smoothed)

	to_return = []
	for i in arange(len(y)):
		if (abs(y[i]-smoothed[i])>2.5*stan_dev):
			to_return.append(smoothed[i])
		else:
			to_return.append(y[i])
	return to_return

my_images = my_dict['andor/image']
#hist(my_images.flatten(),bins=arange(2400,3000,3))	#histogram with no filtering
hist(my_images.flatten(),bins=100)	#histogram with no filtering
my_noise = outlier_removal(my_images.flatten(),window_size)	#just looking at the noise
hist(my_noise,bins=arange(2400,3000,3))



	

window_size = 11
my_noise_spectrum = sum([abs(fft(outlier_removal(i,window_size)))**2 for i in my_images],axis=0)	#ok, I have the noise spectrum now
plot(my_noise_spectrum)

def wiener_filter(signal,signal_power_spectrum,noise_power_spectrum):
	#noise_power_spectrum[0] = 0
	return real(ifft(fft(signal)*signal_power_spectrum*1.0/(noise_power_spectrum+signal_power_spectrum)))*sum(1.0/signal_power_spectrum)

filtered_signal = wiener_filter(my_images[20],1.0,my_noise_spectrum)

filtered_signal_list = array([wiener_filter(i,1.0,my_noise_spectrum) for i in my_images])

plot(sum(filtered_signal_list,axis=0))

plot(sum(my_images,axis=0))


hist(filtered_signal_list.flatten(),bins=100)	#histogram with no filtering
