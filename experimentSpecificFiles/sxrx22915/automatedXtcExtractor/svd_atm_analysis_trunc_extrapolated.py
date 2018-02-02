dropped_shots = array([bool(i) for i in myDict['evr']['code_162']])
dropped_tss_projections = myDict['TSS_OPAL'][dropped_shots] 
traceStart = 400
traceStop = -1
svdSize = 10
u,s,vTrunc = svd(dropped_tss_projections[:,traceStart:traceStop])  
u,s,vFull = svd(dropped_tss_projections) 
vTruncExtrapolated = dot(dot(vTrunc[:svdSize],vFull[:svdSize,traceStart:traceStop].transpose()),vFull[:svdSize])


background_subtracted_opal_proj = myDict['TSS_OPAL']-dot(dot(myDict['TSS_OPAL'][:,traceStart:traceStop],vTrunc[:svdSize].transpose()),vTruncExtrapolated[:svdSize])

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
