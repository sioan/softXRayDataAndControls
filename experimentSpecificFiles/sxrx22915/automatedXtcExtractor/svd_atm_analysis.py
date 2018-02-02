dropped_shots = array([bool(i) for i in myDict['evr']['code_162']])
dropped_tss_projections = myDict['TSS_OPAL'][dropped_shots] 
u,s,v = svd(dropped_tss_projections)  
svdSize = 10

background_subtracted_opal_proj = myDict['TSS_OPAL']-dot(dot(myDict['TSS_OPAL'],v[:svdSize].transpose()),v[:svdSize])

background_divided_opal_proj = myDict['TSS_OPAL']/dot(dot(myDict['TSS_OPAL'],v[:svdSize].transpose()),v[:svdSize])

figure(0)
plot(background_subtracted_opal_proj[0])
plot(background_subtracted_opal_proj[1000])
plot(background_subtracted_opal_proj[8000])


traceStart = 0
traceStop = -1
uq,sq,vq = svd(background_subtracted_opal_proj)
#uq,sq,vq = svd((background_divided_opal_proj[:,traceStart:traceStop])) 

reconstructed = dot(dot(background_subtracted_opal_proj,vq[0:8].transpose()),vq[0:8])
#reconstructed = dot(dot(background_divided_opal_proj[:,traceStart:traceStop],vq[0:8].transpose()),vq[0:8])

figure(1)
plot(reconstructed[0])
plot(reconstructed[1000])
plot(reconstructed[8000])
