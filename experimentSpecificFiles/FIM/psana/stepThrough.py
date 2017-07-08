eventNumber,myEvent  = next(enumeratedEvents)
MCP = kbFluorescenceMontior(myEvent)[0][3]
myImage = imagingDetectorObject.image(myEvent)
subplot(211)
imshow(myImage)
subplot(212)
plot(MCP)
print eventNumber
show()

