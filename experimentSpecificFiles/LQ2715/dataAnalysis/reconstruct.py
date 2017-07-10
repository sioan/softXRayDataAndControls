U, s, V = np.linalg.svd(myData, full_matrices=False)
U.shape, V.shape, s.shape
S = np.diag(s)
S[3:,3:] = 0
S[0,0] = 0
myReconstructedData = np.dot(U, np.dot(S, V))

plot(-myReconstructedData.transpose())
ylim(-20,10)
twinx()
plot(-v[0])
ylim(0,1)
show()
