import numpy as np


def rayleigh(w0, wavelength):
    return np.pi * w0**2 / (wavelength * 1e-6)

def waistFromRayleigh(ray, wavelength):
    return np.sqrt(ray * wavelength * 1e-6 / np.pi)

def beam_radius(w0, zR, z, offset=0):
    return w0 * np.sqrt(1 + ((z - offset) / zR)**2)

def sNew(f, s, zR):
    if f == s:
        sNew = s
    else:
        sNew = f * (s + zR**2 / (s-f)) / (s + zR**2 / (s-f) - f)
    return sNew

def sNew2(f, s, zR):
    sNew = f * (s + zR**2 / (s+f)) / (s + zR**2 / (s+f) + f)
    return sNew

def newWaist(w0, f, s, zR):
    if f != s:
        wNew = w0 * np.abs(f / (s-f)) / np.sqrt(1 + (zR/(s-f))**2)
    else:
        wNew = newWaist2(w0, f, s, zR)
    return wNew

def newWaist2(w0, f, s, zR):
    wNew = w0 / np.sqrt((1 - s/f)**2 + (zR/f)**2)
    return wNew

def theta(w0, zR, parent=None):
    # print(parent, np.arctan(w0 / zR) * 1e3)
    return np.arctan(w0 / zR) * 1e3



def beam_with_lenses(pos, focus, axes, beam_start, sampling=100, start=0, end=100):
    secs = len(focus)
    zs = np.full((sampling, secs + 1), np.nan)

    w0_x, w0_y = beam_start[0], beam_start[1]
    rayX, rayY = beam_start[2], beam_start[3]
    z0_x, z0_y = beam_start[4], beam_start[5]

    wavelength = beam_start[6]


    i = 0
    for sec in pos:
        zs_Sec = np.linspace(start, sec, sampling)
        zs[:, i] = zs_Sec
        start = zs_Sec[-1]
        i += 1

    zs[:, -1] = np.linspace(start, end, sampling)

    radsX = np.zeros_like(zs)
    radsY = np.zeros_like(zs)

    radsX[:, 0] = beam_radius(w0_x, rayX, zs[:, 0], offset=z0_x)
    radsY[:, 0] = beam_radius(w0_y, rayY, zs[:, 0], offset=z0_y)


    for i in range(0, zs.shape[1] - 1):
        f = focus[i]
        beams = axes[i]

        if beams == 'both':
            sX = pos[i] - z0_x
            sY = pos[i] - z0_y

            # print(f'Focus, sX, sY: {f, sX, sY}')

            sNew_x = sNew(f, sX, rayX)
            sNew_y = sNew(f, sY, rayY)

            z0_x = z0_x + sX + sNew_x
            z0_y = z0_y + sY + sNew_y

            # print(f'Focus, zX, zY: {f, z0_x, z0_y}')
            #
            # print(f'Focus, wX, wY, zRx, zRy: {f, w0_x, w0_y, rayX, rayY}')

            w0_x = newWaist(w0_x, f, sX, rayX)
            w0_y = newWaist(w0_y, f, sY, rayY)

            rayX = rayleigh(w0_x, wavelength)
            rayY = rayleigh(w0_y, wavelength)

            # print(f'NEW: Focus, wX, wY, zRx, zRy: {f, w0_x, w0_y, rayX, rayY}')

            radsX[:, i + 1] = beam_radius(w0_x, rayX, zs[:, i + 1], offset=z0_x)
            radsY[:, i + 1] = beam_radius(w0_y, rayY, zs[:, i + 1], offset=z0_y)

        elif beams == 'x':
            sX = pos[i] - z0_x

            sNew_x = sNew(f, sX, rayX)
            z0_x = z0_x + sX + sNew_x
            w0_x = newWaist(w0_x, f, sX, rayX)
            rayX = rayleigh(w0_x, wavelength)

            radsX[:, i + 1] = beam_radius(w0_x, rayX, zs[:, i + 1], offset=z0_x)
            radsY[:, i + 1] = beam_radius(w0_y, rayY, zs[:, i + 1], offset=z0_y)

        elif beams == 'y':
            sY = pos[i] - z0_y
            sNew_y = sNew(f, sY, rayY)

            z0_y = z0_y + sY + sNew_y
            w0_y = newWaist(w0_y, f, sY, rayY)
            rayY = rayleigh(w0_y, wavelength)

            radsX[:, i + 1] = beam_radius(w0_x, rayX, zs[:, i + 1], offset=z0_x)
            radsY[:, i + 1] = beam_radius(w0_y, rayY, zs[:, i + 1], offset=z0_y)


        # print()
        # print('-----')


    # radsX[:, -1] = beam_radius(w0_x, rayX, zs[:, -1], offset=z0_x)
    # radsY[:, -1] = beam_radius(w0_y, rayY, zs[:, -1], offset=z0_y)

    # print()
    # print('===========')
    # print(radsX.flatten(order='F'))
    # print('--------------------------')
    # print(radsY.flatten(order='F'))
    # print(zs.flatten(order='F'))

    return zs.flatten(order='F'), radsX.flatten(order='F'), radsY.flatten(order='F')


def get_pams(pos, focus, axes, beam_start, sampling=100, start=0, end=100):
    secs = len(focus)

    # print(f'Focus: {secs}')

    w0_x, w0_y = beam_start[0], beam_start[1]
    rayX, rayY = beam_start[2], beam_start[3]
    z0_x, z0_y = beam_start[4], beam_start[5]
    wavelength = beam_start[6]

    lasers = []

    waistsX = []
    waistsY = []

    zRs_X = []
    zRs_Y = []

    z0s_X = []
    z0s_Y = []

    dvs_X = []
    dvs_Y = []

    waistsX.append(w0_x)
    waistsY.append(w0_y)

    zRs_X.append(rayX)
    zRs_Y.append(rayY)

    z0s_X.append(z0_x)
    z0s_Y.append(z0_y)

    dvs_X.append(theta(z0_x, rayX))
    dvs_Y.append(theta(z0_y, rayY))


    if len(focus) == 0:
        dc = {'waist_X': waistsX[0], 'waist_Y': waistsY[0], 'ray_X': zRs_X[0], 'ray_Y': zRs_Y[0], 'z0_X': z0s_X[0],
              'z0_Y': z0s_Y[0], 'divergence_X': dvs_X[0], 'divergence_Y': dvs_Y[0], 'wavelength': wavelength}

        lasers.append(dc)

        return lasers, (z0s_X, z0s_Y, waistsX, waistsY, zRs_X, zRs_Y)


    for i in range(0, secs):
        # print(f'section {i}')
        f = focus[i]
        beams = axes[i]

        if beams == 'both':
            sX = pos[i] - z0_x
            sY = pos[i] - z0_y

            sNew_x = sNew(f, sX, rayX)
            sNew_y = sNew(f, sY, rayY)

            z0_x = z0_x + sX + sNew_x
            z0_y = z0_y + sY + sNew_y

            w0_x = newWaist(w0_x, f, sX, rayX)
            w0_y = newWaist(w0_y, f, sY, rayY)

            rayX = rayleigh(w0_x, wavelength)
            rayY = rayleigh(w0_y, wavelength)

            waistsX.append(w0_x)
            waistsY.append(w0_y)

            zRs_X.append(rayX)
            zRs_Y.append(rayY)

            z0s_X.append(z0_x)
            z0s_Y.append(z0_y)

            dvs_X.append(theta(z0_x, rayX))
            dvs_Y.append(theta(z0_y, rayY))

        elif beams == 'x':
            sX = pos[i] - z0_x

            sNew_x = sNew(f, sX, rayX)

            z0_x = z0_x + sX + sNew_x

            w0_x = newWaist(w0_x, f, sX, rayX)

            rayX = rayleigh(w0_x, wavelength)

            waistsX.append(w0_x)
            waistsY.append(np.nan)

            zRs_X.append(rayX)
            zRs_Y.append(np.nan)

            z0s_X.append(z0_x)
            z0s_Y.append(np.nan)

            dvs_X.append(theta(z0_x, rayX))
            dvs_Y.append(np.nan)


        elif beams == 'y':
            sY = pos[i] - z0_y

            sNew_y = sNew(f, sY, rayY)
            z0_y = z0_y + sY + sNew_y
            w0_y = newWaist(w0_y, f, sY, rayY)
            rayY = rayleigh(w0_y, wavelength)

            waistsX.append(np.nan)
            waistsY.append(w0_y)

            zRs_X.append(np.nan)
            zRs_Y.append(rayY)

            z0s_X.append(np.nan)
            z0s_Y.append(z0_y)

            dvs_X.append(np.nan)
            dvs_Y.append(theta(z0_y, rayY))


    zRs_X.append(rayX)
    zRs_Y.append(rayY)

    z0s_X.append(z0_x)
    z0s_Y.append(z0_y)

    dvs_X.append(theta(z0_x, rayX))
    dvs_Y.append(theta(z0_y, rayY))

    for i in range(len(waistsX)):
        dc = {'waist_X': waistsX[i], 'waist_Y': waistsY[i], 'ray_X': zRs_X[i], 'ray_Y': zRs_Y[i], 'z0_X': z0s_X[i],
              'z0_Y': z0s_Y[i], 'divergence_X': dvs_X[i], 'divergence_Y': dvs_Y[i], 'wavelength': wavelength}

        lasers.append(dc)

    return lasers, (z0s_X, z0s_Y, waistsX, waistsY, zRs_X, zRs_Y)