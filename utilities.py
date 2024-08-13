import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.pyplot as plt

from PyQt5.QtGui import QPixmap, QImage

from io import BytesIO
import sys, os


plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
plt.rcParams['mathtext.default'] = 'regular'


def find_missing(lst):
    minM = min(lst)
    maxM = max(lst)

    missing = maxM + 1
    list1 = []

    for _ in lst:
        maxM = maxM - 1
        if maxM not in lst:
            list1.append(maxM)

    return list1


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def math2svg( mathTex, fontsize=12, dpi=300):
    print('Formula')

    fig = plt.figure()
    fig.text(0, 0, r'${}$'.format(mathTex), fontsize=fontsize)

    output = BytesIO()
    fig.savefig(output, dpi=dpi, transparent=True, format='svg',
                bbox_inches='tight', pad_inches=0.0)
    plt.close(fig)

    output.seek(0)
    return output.read()


def mathTex_to_QPixmap(mathTex, fs):
    # ---- set up a mpl figure instance ----

    fig = matplotlib.figure.Figure()
    fig.patch.set_facecolor('none')
    fig.set_canvas(FigureCanvasAgg(fig))
    renderer = fig.canvas.get_renderer()

    # ---- plot the mathTex expression ----

    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.patch.set_facecolor('none')
    t = ax.text(0, 0, mathTex, horizontalalignment='left', verticalalignment='bottom', fontsize=fs, fontdict=None)

    # ---- fit figure size to text artist ----

    fwidth, fheight = fig.get_size_inches()
    fig_bbox = fig.get_window_extent(renderer)

    text_bbox = t.get_window_extent(renderer)

    tight_fwidth = text_bbox.width * fwidth / fig_bbox.width
    tight_fheight = text_bbox.height * fheight / fig_bbox.height

    fig.set_size_inches(tight_fwidth, tight_fheight)

    # ---- convert mpl figure to QPixmap ----

    buf, size = fig.canvas.print_to_buffer()
    qimage = QImage.rgbSwapped(QImage(buf, size[0], size[1], QImage.Format_ARGB32))
    qpixmap = QPixmap(qimage)

    return qpixmap

