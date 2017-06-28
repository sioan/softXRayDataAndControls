#singular value decomposition
#u,s,v = svd(monoExitSlitYagSpectrum,full_matrices=False)

#reconstruction
S = diag(s)
S[50:,50:] = 0
reconstructedMonoExitSlitYagSpectrum = dot(u,dot(S,v))

#plotting

myRandomNumber = int(579*rand())

plot(monoExitSlitYagSpectrum[myRandomNumber],'r.')
plot(reconstructedMonoExitSlitYagSpectrum[myRandomNumber])
