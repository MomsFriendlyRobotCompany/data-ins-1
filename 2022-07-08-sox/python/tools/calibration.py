# from numpy import linalg
# import scipy
import numpy as np
import pickle
# from colorama import Fore
# from matplotlib import pyplot as plt

# def printdict(d,space=0):
#     if space == 0:
#         color = Fore.BLUE
#     elif space == 2:
#         color = Fore.MAGENTA
#     else:
#         color = Fore.GREEN

#     for k,v in d.items():
#         print(f"{' '*space}{color}{k}:{Fore.RESET}")
#         if isinstance(v, dict):
#             printdict(v, space+2)
#         elif isinstance(v, tuple):
#             for i in v:
#                 print(f"{' '*(space+2)}{i}")
#         else:
#             print(f"{' '*(space+2)}{v}")


def gravity(lat):
    """Based off the Oxford reference for the gravity formula at sealevel.
    https://www.oxfordreference.com/view/10.1093/oi/authority.20110803100007626

    lat: latitude in degrees
    """
    lat *= np.pi/180
    return 9.78*(1 + 0.0053024*np.sin(lat)**2 - 0.0000058*np.sin(2*lat)**2)

def get_ideal(orient, num):
    """
    Given an orientation, calculate the ideal local gravity vector
    """
    g = 1.0
    if orient == "x-up":
        nn=np.array([g,0,0]*num).reshape(num,3)
    elif orient == "x-down":
        nn=np.array([-g,0,0]*num).reshape(num,3)
    elif orient == "y-up":
        nn=np.array([0,g,0]*num).reshape(num,3)
    elif orient == "y-down":
        nn=np.array([0,-g,0]*num).reshape(num,3)
    elif orient == "z-up":
        nn=np.array([0,0,g]*num).reshape(num,3)
    elif orient == "z-down":
        nn=np.array([0,0,-g]*num).reshape(num,3)
    else:
        raise Exception("Invalid orientation")

    return nn

def least_squares_fit(A, B):
    """B = A*x which is: ideal = noisy*x => [n,3] = [n,4][4,3]
    ideal = [n,3] = [x,y,z]
    noisy = [n,4] = [x,y,z,1]: the 1 accounts for the biases
    A = [4,3]: this is a bunch of coefficient matrices [[S],[H]]
      S = [3,3]
      H = [1,3]
    """
    # Need to extend A and B
    # A = np.hstack((A, np.ones(len(A)).reshape(-1, 1)))
    # print(A)

    X, res, rank, s = np.linalg.lstsq(A, B, rcond=None)
    print(f"Rank: {rank}")
    print(f"Singular values: {s}")
    print(f"Sum residual error: {np.sum(res)}")
    return X

def calcCorrection(noisey, axisOrder):
    sz = noisey.shape
    noisey = np.concatenate((noisey, np.ones((sz[0],1))), axis=1)
    ideal = None
    for axis in axisOrder:
        i = get_ideal(axis, sz[0]//6)
        if ideal is None:
            ideal = i
        else:
            ideal = np.concatenate((ideal, i), axis=0)

    xx = least_squares_fit(noisey, ideal)
    print("--------------------------------")
    print(xx)
    return xx

def correct(noisey, xx):
    sz = noisey.shape
    a = np.concatenate((noisey, np.ones((sz[0],1))), axis=1)
    return a.dot(xx)

#=============================================================

# def ellipticalFit(s, F=1):
#     ''' Performs calibration of magnetometer data by performing an
#     elliptical fit of the data.

#     References
#     ----------
#     .. [1] Qingde Li; Griffiths, J.G., "Least squares ellipsoid specific
#        fitting," in Geometric Modeling and Processing, 2004.
#        Proceedings, vol., no., pp.335-340, 2004

#     https://www.researchgate.net/publication/4070857_Least_squares_ellipsoid_specific_fitting

#     F: expected field strength, default is 1
#     Returns: an A and b matrix, such that, actual_mag = A*noisy_mag + b
#     '''
#     s = s.T

#     # D (samples)
#     D = np.array([
#         s[0]**2., s[1]**2., s[2]**2.,
#         2.*s[1]*s[2], 2.*s[0]*s[2], 2.*s[0]*s[1],
#         2.*s[0], 2.*s[1], 2.*s[2], np.ones_like(s[0])])

#     # S, S_11, S_12, S_21, S_22 (eq. 11)
#     S = np.dot(D, D.T)
#     S_11 = S[:6,:6]
#     S_12 = S[:6,6:]
#     S_21 = S[6:,:6]
#     S_22 = S[6:,6:]

#     # C (Eq. 8, k=4)
#     C = np.array([[-1,  1,  1,  0,  0,  0],
#                   [ 1, -1,  1,  0,  0,  0],
#                   [ 1,  1, -1,  0,  0,  0],
#                   [ 0,  0,  0, -4,  0,  0],
#                   [ 0,  0,  0,  0, -4,  0],
#                   [ 0,  0,  0,  0,  0, -4]])

#     # v_1 (eq. 15, solution)
#     E = np.dot(
#         np.linalg.inv(C),
#         S_11 - np.dot(S_12, np.dot(np.linalg.inv(S_22), S_21)))

#     E_w, E_v = np.linalg.eig(E)

#     v_1 = E_v[:, np.argmax(E_w)]
#     if v_1[0] < 0: v_1 = -v_1

#     # v_2 (eq. 13, solution)
#     v_2 = np.dot(np.dot(-np.linalg.inv(S_22), S_21), v_1)

#     # quadric-form parameters
#     M = np.array([[v_1[0], v_1[3], v_1[4]],
#                   [v_1[3], v_1[1], v_1[5]],
#                   [v_1[4], v_1[5], v_1[2]]])
#     n = np.array([[v_2[0]],
#                   [v_2[1]],
#                   [v_2[2]]])
#     d = v_2[3]

#     #-------------------------------------
#     # calibration parameters
#     # note: some implementations of sqrtm return complex type, taking real
#     M_1 = np.linalg.inv(M)
#     b = -np.dot(M_1, n).T[0]  # make numpy array [bx,by,bz]

#     A = F / np.sqrt(np.abs(np.dot(n.T, np.dot(M_1, n)) - d))
#     A = A*np.real(scipy.linalg.sqrtm(M))

#     return A, b

def magcal(Bp, uT=None):
    """
    Modelled after the matlab function: magcal(D) -> A, b, expmfs
    inputs:
        Bp: data points
        uT: expected field strength for longitude/altitude. If None
            is given, then automatically calculated and used
    returns:
        A: soft-iron 3x3 matrix of scaling
        b: hard-iron offsets
        expmfs: expected field strength
    """
    Y = np.array([v[0]**2+v[1]**2+v[2]**2 for v in Bp])
    X = np.hstack((Bp,np.ones((Bp.shape[0],1))))
    beta = np.linalg.inv(X.T.dot(X)).dot(X.T.dot(Y))
    b=0.5*beta[:3]

    # expected mag field strength
    expmfs=np.sqrt(beta[3]+b[0]**2+b[1]**2+b[2]**2)

    if uT is None:
        uT = expmfs

    x = [v[0] for v in Bp]
    rx = (max(x)-min(x))/2

    y = [v[1] for v in Bp]
    ry = (max(y)-min(y))/2

    z = [v[2] for v in Bp]
    rz = (max(z)-min(z))/2

    A = np.diag([uT/rx,uT/ry,uT/rz])
    return A,b,expmfs

# def ellipticaleigen(Bpp):
#     """
#     D = [X2, Y2, Z2, 2XY,2XZ, 2YZ, 2X, 2Y, 2Z]
#     v = [ a, b, c, d, e, f, g, h, i ]
#     1 [Nx1]
#     v[9x1] = inv(DT D)[9x9] (DT 1)[9x1]

#     A = [
#         v(1) v(4) v(5) v(7);
#         v(4) v(2) v(6) v(8);
#         v(5) v(6) v(3) v(9);
#         v(7) v(8) v(9) -1 ];
#     ofs=-A(1:3,1:3)\[v(7);v(8);v(9)]; % offset is center of ellipsoid
#     Tmtx=eye(4);
#     Tmtx(4,1:3)=ofs';
#     AT=Tmtx*A*Tmtx'; % ellipsoid translated to (0,0,0)
#     [rotM ev]=eig(AT(1:3,1:3)/-AT(4,4)); % eigenvectors (rotation) and eigenvalues (gain)
#     gain=sqrt(1./diag(ev)); % gain is radius of the ellipsoid
#     """
#     x = Bpp[:,0]
#     y = Bpp[:,1]
#     z = Bpp[:,2]
#     sz = len(Bpp)
#     D = np.array([x*x,y*y,z*z,2*x*y,2*x*z,2*y*z,2*x,2*y,2*z]).T
#     v = np.linalg.inv(D.T @ D) @ (D.T @ np.ones(sz))
#     print(v)
#     A = np.array([
#         [v[0], v[3], v[4], v[6]],
#         [v[3], v[1], v[5], v[7]],
#         [v[4], v[5], v[2], v[8]],
#         [v[6], v[7], v[8],   -1]
#     ])

#     ofs=-np.linalg.inv(A[:3,:3]) @ np.array([v[6], v[7], v[8]]).T
#     Tmtx = np.eye(4)
#     Tmtx[3,:3] = ofs
#     AT = Tmtx @ A @ Tmtx.T
#     ev, rotM = np.linalg.eig(AT[:3,:3]/-AT[3,3])
#     gain = np.sqrt(1/ev)  # added abs, negative sqrt values

#     print(f"gain: {gain}")
#     print(f"offsets: {ofs}")
#     print(f"rot mat: \n {rotM}")
#     return gain, ofs, rotM
