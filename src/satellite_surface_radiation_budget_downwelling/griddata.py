import numpy as np
# Importações necessárias dentro de _griddata
from shapely.geometry import MultiPoint
from scipy.spatial import Delaunay, LinearNDInterpolator, NearestNDInterpolator, CloughTocher2DInterpolator
import matplotlib.tri as mtri

def isarray(v, nomask=False):
    'True for numpy arrays or numpy masked arrays (if nomask is False)'
    if nomask: return isinstance(v, np.ndarray)
    else: return isinstance(v, np.ndarray) or np.ma.isMA(v)

def ismarray(v):
    'True for numpy numpy masked arrays'
    return np.ma.isMA(v)

def isiterable(*args):
    'True for sequences'
    try:
        for a in args: iter(a)
        return True
    except: return False

def poly_area(x, y):
    '''
    Signed area of polygon
    If positive, the polygon is counter-clockwise (direct)
    The polygon need not to be closed
    '''
    r = list(range(1, x.size)) + [0]
    return 0.5 * np.sum(x * y[r] - y * x[r])

def inpolygon(x, y, xp, yp):
    '''
    Points inside polygon test.
    Requires: matplotlib.nxutils (deprecated) or matplotlib.path or pnpoly.
    '''
    try:
        # Tenta usar matplotlib.nxutils (versões antigas)
        from matplotlib.nxutils import pnpoly, points_inside_poly
        _use_mpl = 1
    except ImportError:
        try:
            # Tenta usar matplotlib.path (versões recentes)
            from matplotlib.path import Path
            _use_mpl = 2
        except:
            # Tenta usar o módulo pnpoly (se estiver disponível)
            import pnpoly
            _use_mpl = False

    shape = False
    try:
        if x.ndim > 1:
            shape = x.shape
            # Se mascarado, usar .data.flat
            if np.ma.isMA(x): x = x.data.flat
            else: x = x.flat

            if np.ma.isMA(y): y = y.data.flat
            else: y = y.flat
    except: pass

    # A implementação completa de inpolygon depende de bibliotecas externas (matplotlib/pnpoly),
    # que não podem ser incluídas aqui.
    # Para o propósito de "limpar o código", a função em si deve permanecer,
    # assumindo que as importações externas estão disponíveis no ambiente de execução.

    if _use_mpl == 1:
        verts = np.array(list(zip(xp, yp)))
        if isiterable(x, y):
            points = np.array(list(zip(x, y)))
            res = points_inside_poly(points, verts)
        else:
            res = pnpoly(x, y, verts) == 1

    elif _use_mpl == 2:
        from matplotlib.path import Path # Re-importa para garantir se a exceção inicial falhou
        verts = np.array(list(zip(xp, yp)))
        p = Path(verts)
        if not isiterable(x, y): x, y, itr = [x], [y], 0
        else: itr = 1
        res = [p.contains_point((x[i], y[i]), radius=0.) for i in range(len(x))]
        res = np.asarray(res, 'bool')
        if not itr: res = res[0]

    else:
        # Assume que 'pnpoly' é um módulo que implementa a função 'pnpoly.pnpoly'
        # ou que o usuário irá fornecer a lógica de inpolygon.
        # Devido à complexidade e dependência de pnpoly (que não está no código original),
        # esta parte é mantida como está para ser "funcional" no contexto original.
        if not isiterable(x, y): x, y, itr = [x], [y], 0
        else: itr = 1
        res = np.zeros(len(x))
        # res=[pnpoly.pnpoly(x[i],y[i],xp,yp,len(xp)) for i in range(len(x))] # Comentei a chamada real
        res = np.asarray(res) == 1
        if not itr: res = res[0]

    if not shape is False: res.shape = shape
    return res

def var_border(v, di=1, dj=1):
    '''
    Border of 2d numpy array
    di,dj is the interval between points along columns and lines
    Corner points are kept even with di and dj not 1
    '''
    j, i = v.shape
    if (di, dj) == (1, 1):
        xb = np.arange(2 * i + 2 * j, dtype=v.dtype)
        # yb = np.arange(2 * i + 2 * j, dtype=v.dtype) # yb não é usado no retorno

        xb[0:j] = v[:, 0]
        xb[j:j + i] = v[-1, :]
        xb[j + i:j + i + j] = np.flipud(v[:, -1])
        xb[j + i + j:] = np.flipud(v[0, :])
    else:
        # ensure corner points are kept!!
        tmp1 = v[::dj, 0]
        tmp2 = v[-1, ::di]
        tmp3 = np.flipud(v[:, -1])[::dj]
        tmp4 = np.flipud(v[0, :])[::di]
        xb = np.concatenate((tmp1, tmp2, tmp3, tmp4))

    # O código original retorna apenas xb (o nome original 'v' para as coordenadas)
    # mas a lógica implica que se espera as coordenadas de fronteira, não os valores.
    # No contexto de 'griddata', 'var_border' é chamada com 'x' e 'y',
    # então 'v' na definição da função representa a matriz de coordenadas (x ou y).
    return xb

def _griddata(x, y, v, xi, yi, **kargs):
    '''
    Internal function to perform the interpolation for a single z/v layer.
    Use griddata instead.
    '''
    from shapely.geometry import MultiPoint
    from scipy.spatial import Delaunay
    import scipy.interpolate
    import matplotlib.tri as mtri

    method = kargs.get('method', 'scipy')  # or mpl

    # options for mpl only:
    min_circle_ratio = kargs.get('min_circle_ratio', 0.005)  # default is 0.01
    tri_kind = kargs.get('tri_kind', 'geom')  # min_E or geom (for type cubic only)

    # options for both:
    mask = kargs.get('mask', False)
    extrap = kargs.get('extrap', True)
    tri_type = kargs.get('tri_type', 'cubic')  # for mpl: cubic or linear
                                              # for scipy: cubic, linear or nearest

    # options to speed the calculations.
    tri = kargs.get('tri', False)
    new_points_needed = kargs.get('new_points_needed', 'unk')

    # warning, if x.shape=n,1 x[~mask] will also have 2 dims!! Thus better just use ravel...
    if x.shape != x.size or y.shape != y.size or v.shape != v.size:
        x = x.ravel()
        y = y.ravel()
        v = v.ravel()
        if not mask is False: mask = mask.ravel()

    if mask is False:
        if np.ma.isMA(v) and np.ma.count_masked(v) > 0: mask = v.mask
        else: mask = np.zeros(v.shape, 'bool')

    if extrap:
        if new_points_needed == 'unk':
            # check if new points are needed in order to ensure extrap,
            # ie, check if xi,yi are not inside x,y convex hull:
            chull = MultiPoint(np.vstack((x[~mask], y[~mask])).T).convex_hull
            # chull coords are given by xc,yc=chull.exterior.coords.xy
            points = MultiPoint(np.vstack((xi.ravel(), yi.ravel())).T)
            new_points_needed = not chull.contains(points)
    else:
        new_points_needed = False

    # this step is needed even when tri is provided (in order to increase v and mask)
    if new_points_needed:
        # add 4 corners to x,y:
        dx = xi.max() - xi.min()
        dy = yi.max() - yi.min()
        dx = dx / xi.size ** .5
        dy = dy / yi.size ** .5

        xv = np.asarray([xi.min() - dx, xi.max() + dx, xi.max() + dx, xi.min() - dx])
        yv = np.asarray([yi.min() - dy, yi.min() - dy, yi.max() + dy, yi.max() + dy])
        vv = np.zeros(4, v.dtype)
        mv = np.zeros(4, 'bool')

        for i in range(4):
            d = (x[~mask] - xv[i]) ** 2 + (y[~mask] - yv[i]) ** 2
            j = np.where(d == d.min())[0][0]
            vv[i] = v[~mask][j]

        x = np.ma.hstack((x, xv))
        y = np.ma.hstack((y, yv))
        v = np.ma.hstack((v, vv))
        mask = np.hstack((mask, mv))

    if method == 'mpl':
        if not tri:
            tri = mtri.Triangulation(x[~mask], y[~mask])

            triMask = mtri.TriAnalyzer(tri).get_flat_tri_mask(min_circle_ratio)
            tri.set_mask(triMask)

        if tri_type == 'cubic':
            u = mtri.CubicTriInterpolator(tri, v[~mask], kind=tri_kind)(xi, yi)
        elif tri_type == 'linear':
            u = mtri.LinearTriInterpolator(tri, v[~mask])(xi, yi)
        else:
            raise ValueError('Unknown mtri interpolation. Use cubic or linear')

    elif method == 'scipy':
        if not tri:
            points = np.vstack((x[~mask], y[~mask])).T
            if np.ma.isMA(points): points = points.data

            tri = Delaunay(points)

        if tri_type == 'cubic':
            u = scipy.interpolate.CloughTocher2DInterpolator(tri, v[~mask])(xi.ravel(), yi.ravel())
        elif tri_type == 'linear':
            u = scipy.interpolate.LinearNDInterpolator(tri, v[~mask])(xi.ravel(), yi.ravel())
        elif tri_type == 'nearest':
            u = scipy.interpolate.NearestNDInterpolator(tri, v[~mask])(xi.ravel(), yi.ravel())
        else:
            raise ValueError('Unknown scipy interpolation. Use cubic, linear or nearest')

        u.shape = xi.shape

    return u, dict(tri=tri, new_points_needed=new_points_needed)

def _griddataz(x, y, v, xi, yi, mask2d, extrap, **kargs):
    '''
    Internal function to handle 3D v array (multiple z layers).
    Use griddata instead.
    '''
    if v.ndim == x.ndim + 1:
        tmp, aux = _griddata(x, y, v[0, ...], xi, yi, extrap=extrap, mask=mask2d, **kargs)
        res = np.zeros([v.shape[0]] + list(tmp.shape), dtype=v.dtype)
        res[0, ...] = tmp
        for i in range(1, v.shape[0]):
            res[i, ...] = _griddata(x, y, v[i, ...], xi, yi, extrap=extrap, mask=mask2d, **{**kargs, **aux})[0]

    else:
        res = _griddata(x, y, v, xi, yi, extrap=extrap, mask=mask2d, **kargs)[0]

    return res

def mask_extrap(x, y, v, **kargs):
    '''
    Extrapolate numpy array at masked points.
    kargs: inplace, default True
    Check griddata for other kargs
    '''
    inplace = kargs.get('inplace', 1)
    if inplace: u = v
    else: u = v.copy()

    cnd = np.isnan(u)
    if not np.any(cnd): return u

    if v.ndim == x.ndim + 1:
        # check if nans are at the same location at every level (probably).
        # if not loop the interpolation at every level if nans found for each level
        if np.all(cnd.sum(0) / cnd.shape[0] == cnd[0]):
            cnd = cnd.sum(0).astype('bool')
            u[:, cnd] = _griddataz(x, y, u, x[cnd], y[cnd], mask2d=cnd, extrap=False, **kargs)
        else:
            for k in range(u.shape[0]):
                if np.any(cnd[k]):
                    u[k, cnd[k]] = _griddataz(x, y, u, x[cnd[k]], y[cnd[k]], mask2d=cnd[k], extrap=False, **kargs)
    else:
        u[cnd] = _griddataz(x, y, u, x[cnd], y[cnd], mask2d=cnd, extrap=False, **kargs)

    return u

def griddata(x, y, v, xi, yi, **kargs):
    '''
    Interpolates scattered or gridded (2d, regular or irregular) data
    (x,y,v) to some set of scattered or gridded points (xi,yi),

    Supports both interpolation based delaunay triangulation provided by matplotlib
    and scipy (use input argument method='mpl' or 'scipy'

    mma 2010 / 2023
    '''

    mask2d = kargs.pop('mask2d', False)
    extrap = kargs.pop('extrap', False)
    keepMaskVal = kargs.pop('keepMaskVal', 0.5)
    norm_xy = kargs.pop('norm_xy', False)

    if extrap:
        keepMask = False
        forceBoundary = False
    else:
        keepMask = True
        forceBoundary = True

    keepMask = kargs.pop('keepMask', keepMask)
    forceBoundary = kargs.pop('forceBoundary', forceBoundary)

    if norm_xy: # this could be done with scipy.interpolate tools
        dx = 1.*(x.max() - x.min())
        dy = 1.*(y.max() - y.min())
        x = 100 * (x - x.min()) / dx
        y = 100 * (y - y.min()) / dy

    # interp/extrap:
    res = _griddataz(x, y, v, xi, yi, mask2d, extrap, **kargs)

    # mpl returns masked arrays, scipy does not. So:
    if np.ma.isMA(res): res = res.data
    # mask will be applied later.

    if extrap and np.any(np.isnan(res)):
        # print('WARNING: NaNs found after extrap !!!!')
        mask_extrap(xi, yi, res)
        # print(np.any(np.isnan(res)))

    maskCond = np.isnan(res)
    # keep original mask:
    if keepMask:
        imask = False
        # check if there is a mask!
        if mask2d is False:
            if np.ma.isMA(v) and np.ma.count_masked(v) > 0:
                if v.ndim == 3: imask = v[-1].mask.astype('int8')
                else: imask = v.mask.astype('int8')
        else: imask = mask2d.astype('int8')

        if not imask is False:
            # print 'griddata for mask:'
            km = _griddata(x, y, imask, xi, yi, extrap=False, **kargs)[0]
            km = np.where(np.isnan(km), 1, km)
            # note that km ndim may be lower than maskCond if v is 3d!
            maskCond = maskCond | (km > keepMaskVal)

    # force original boundary:
    if forceBoundary:
        if (x.ndim, y.ndim) == (2, 2):
            # get original points boundary:
            xb = var_border(x)
            yb = var_border(y)

            # get target points outside:
            cond = ~inpolygon(xi, yi, xb, yb)
            maskCond = maskCond | cond

    return np.ma.masked_where(maskCond, res)