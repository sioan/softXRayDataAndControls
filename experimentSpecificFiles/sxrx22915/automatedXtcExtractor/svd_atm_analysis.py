dropped_shots = array([bool(i) for i in myDict['evr']['code_162']])
dropped_tss_projections = myDict['TSS_OPAL'][dropped_shots] 
u,s,v = svd(dropped_tss_projections)  
svdSize = 10

background_subtracted_opal_proj = myDict['TSS_OPAL']-dot(dot(myDict['TSS_OPAL'],v[:svdSize].transpose()),v[:svdSize])

background_divided_opal_proj = myDict['TSS_OPAL']/dot(dot(myDict['TSS_OPAL'],v[:svdSize].transpose()),v[:svdSize])

uq,sq,vq = svd(background_subtracted_opal_proj) 


reconstructed = dot(dot(background_subtracted_opal_proj,vq[1:8].transpose()),vq[1:8])

plot(reconstructed[0])
plot(reconstructed[1000])
plot(reconstructed[8000])
