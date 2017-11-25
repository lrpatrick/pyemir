from __future__ import division
from __future__ import print_function

from astropy.io import fits
from copy import deepcopy

from emirdrp.core import EMIR_NBARS


class CsuConfiguration(object):
    """Configurable Slit Unit (CSU) Configuration class definition.

    Attributes
    ----------
    _csu_bar_left : list of floats
        Location (mm) of the left bar for each slitlet.
    _csu_bar_right : list of floats
        Location (mm) of the right bar for each slitlet, using the
        same origin employed for _csu_bar_left (which is not the
        value stored in the FITS keywords.
    _csu_bar_slit_center : list of floats
        Middle point (mm) in between the two bars defining a slitlet.
    _csu_bar_slit_width : list of floats
        Slitlet width (mm), computed as the distance between the two
        bars defining the slitlet.
    _defined : bool
        Indicates whether the CSU parameters have been properly defined.

    """

    def __init__(self):
        self._csu_bar_left = None
        self._csu_bar_right = None
        self._csu_bar_slit_center = None
        self._csu_bar_slit_width = None
        self._defined = False

    def __str__(self):
        output = "<CsuConfiguration instance>\n"
        for i in range(EMIR_NBARS):
            ibar = i + 1
            strdum = "- [BAR{0:2d}] left, right, center, width: ".format(ibar)
            output += strdum
            if self._defined:
                strdum = "{0:7.3f} {1:7.3f} {2:7.3f} {3:7.3f}\n".format(
                    self._csu_bar_left[i], self._csu_bar_right[i],
                    self._csu_bar_slit_center[i], self._csu_bar_slit_width[i]
                )
                output += strdum
            else:
                output += 4 * "   None " + "\n"
        return output

    def __eq__(self, other):
        result = \
            (self._defined == other._defined) and \
            (self._csu_bar_left == other._csu_bar_left) and \
            (self._csu_bar_right == other._csu_bar_right) and \
            (self._csu_bar_slit_center == other._csu_bar_slit_center) and \
            (self._csu_bar_slit_width == other._csu_bar_slit_width)
        return result

    def define_from_fits(self, fitsobj, extnum=0):
        """Define class members from header information in FITS file.

        Parameters
        ----------
        fitsobj: file object
            FITS file whose header contains the CSU bar information
            needed to initialise the members of this class.
        extnum : int
            Extension number (first extension is 0)

        """

        # read input FITS file
        with fits.open(fitsobj) as hdulist:
            image_header = hdulist[extnum].header

        # declare arrays to store configuration of CSU bars
        self._csu_bar_left = []
        self._csu_bar_right = []
        self._csu_bar_slit_center = []
        self._csu_bar_slit_width = []

        for i in range(EMIR_NBARS):
            ibar = i + 1
            keyword = 'CSUP{}'.format(ibar)
            if keyword in image_header:
                self._csu_bar_left.append(image_header[keyword])
            else:
                raise ValueError("Expected keyword " + keyword + " not found!")
            keyword = 'CSUP{}'.format(ibar + EMIR_NBARS)
            if keyword in image_header:
                # set the same origin as the one employed for _csu_bar_left
                self._csu_bar_right.append(341.5 - image_header[keyword])
            else:
                raise ValueError("Expected keyword " + keyword + " not found!")
            self._csu_bar_slit_center.append(
                (self._csu_bar_left[i] + self._csu_bar_right[i]) / 2
            )
            self._csu_bar_slit_width.append(
                self._csu_bar_right[i] - self._csu_bar_left[i]
            )

        # the attributes have been properly set
        self._defined = True

    def csu_bar_left(self, islitlet):
        """Return csu_bar_left for requested slitlet number."""

        return self._csu_bar_left[islitlet - 1]

    def csu_bar_right(self, islitlet):
        """Return csu_bar_right for requested slitlet number."""

        return self._csu_bar_right[islitlet - 1]

    def csu_bar_slit_center(self, islitlet):
        """Return csu_bar_slit_center for requested slitlet number."""

        return self._csu_bar_slit_center[islitlet - 1]

    def csu_bar_slit_width(self, islitlet):
        """Return csu_bar_slit_width for requested slitlet number."""

        return self._csu_bar_slit_width[islitlet - 1]

    def outdict(self):
        """Return dictionary structure rounded to a given precision."""

        outdict = {}
        if self._defined:
            for i in range(EMIR_NBARS):
                ibar = i + 1
                cbar = 'slitlet' + str(ibar).zfill(2)
                outdict[cbar] = {}
                outdict[cbar]['_csu_bar_left'] = \
                    round(self._csu_bar_left[i], 3)
                outdict[cbar]['_csu_bar_right'] = \
                    round(self._csu_bar_right[i], 3)
                outdict[cbar]['_csu_bar_slit_center'] = \
                    round(self._csu_bar_slit_center[i], 3)
                outdict[cbar]['_csu_bar_slit_width'] = \
                    round(self._csu_bar_slit_width[i], 3)

        return outdict


def merge_odd_even_csu_configurations(conf_odd, conf_even):
    """Merge CSU configuration using odd- and even-numbered values.

    The CSU returned CSU configuration include the odd-numbered values
    from 'conf_odd' and the even-numbered values from 'conf_even'.

    Parameters
    ----------
    conf_odd : CsuConfiguration instance
        CSU configuration corresponding to odd-numbered slitlets.
    conf_even : CsuConfiguration instance
        CSU configuration corresponding to even-numbered slitlets.

    Returns
    -------
    merged_conf : CsuConfiguration instance
        CSU configuration resulting from the merging process.

    """

    # initialize resulting CsuConfiguration instance using one of the
    # input configuration corresponding to the odd-numbered slitlets
    merged_conf = deepcopy(conf_odd)

    # update the resulting configuration with the values corresponding
    # to the even-numbered slitlets
    for i in range(EMIR_NBARS):
        ibar = i + 1
        if ibar % 2 == 0:
            merged_conf._csu_bar_left[i] = conf_even._csu_bar_left[i]
            merged_conf._csu_bar_right[i] = conf_even._csu_bar_right[i]
            merged_conf._csu_bar_slit_center[i] = \
                conf_even._csu_bar_slit_center[i]
            merged_conf._csu_bar_slit_width[i] = \
                conf_even._csu_bar_slit_width[i]

    # return merged configuration
    return merged_conf