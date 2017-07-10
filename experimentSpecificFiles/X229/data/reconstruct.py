U, s, V = np.linalg.svd(myData, full_matrices=False)
U.shape, V.shape, s.shape
S = np.diag(s)
S[3:,3:] = 0
myReconstructedData = np.dot(U, np.dot(S, V))

