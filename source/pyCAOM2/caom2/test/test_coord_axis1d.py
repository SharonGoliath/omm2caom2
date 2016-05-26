#!/usr/bin/env python
# -*- coding: utf-8 -*-
#***********************************************************************
#******************  CANADIAN ASTRONOMY DATA CENTRE  *******************
#*************  CENTRE CANADIEN DE DONNÉES ASTRONOMIQUES  **************
#
#  (c) 2010.                            (c) 2010.
#  Government of Canada                 Gouvernement du Canada
#  National Research Council            Conseil national de recherches
#  Ottawa, Canada, K1A 0R6              Ottawa, Canada, K1A 0R6
#  All rights reserved                  Tous droits réservés
#
#  NRC disclaims any warranties,        Le CNRC dénie toute garantie
#  expressed, implied, or               énoncée, implicite ou légale,
#  statutory, of any kind with          de quelque nature que ce
#  respect to the software,             soit, concernant le logiciel,
#  including without limitation         y compris sans restriction
#  any warranty of merchantability      toute garantie de valeur
#  or fitness for a particular          marchande ou de pertinence
#  purpose. NRC shall not be            pour un usage particulier.
#  liable in any event for any          Le CNRC ne pourra en aucun cas
#  damages, whether direct or           être tenu responsable de tout
#  indirect, special or general,        dommage, direct ou indirect,
#  consequential or incidental,         particulier ou général,
#  arising from the use of the          accessoire ou fortuit, résultant
#  software.  Neither the name          de l'utilisation du logiciel. Ni
#  of the National Research             le nom du Conseil National de
#  Council of Canada nor the            Recherches du Canada ni les noms
#  names of its contributors may        de ses  participants ne peuvent
#  be used to endorse or promote        être utilisés pour approuver ou
#  products derived from this           promouvoir les produits dérivés
#  software without specific prior      de ce logiciel sans autorisation
#  written permission.                  préalable et particulière
#                                       par écrit.
#
#  This file is part of the             Ce fichier fait partie du projet
#  OpenCADC project.                    OpenCADC.
#
#  OpenCADC is free software:           OpenCADC est un logiciel libre ;
#  you can redistribute it and/or       vous pouvez le redistribuer ou le
#  modify it under the terms of         modifier suivant les termes de
#  the GNU Affero General Public        la “GNU Affero General Public
#  License as published by the          License” telle que publiée
#  Free Software Foundation,            par la Free Software Foundation
#  either version 3 of the              : soit la version 3 de cette
#  License, or (at your option)         licence, soit (à votre gré)
#  any later version.                   toute version ultérieure.
#
#  OpenCADC is distributed in the       OpenCADC est distribué
#  hope that it will be useful,         dans l’espoir qu’il vous
#  but WITHOUT ANY WARRANTY;            sera utile, mais SANS AUCUNE
#  without even the implied             GARANTIE : sans même la garantie
#  warranty of MERCHANTABILITY          implicite de COMMERCIALISABILITÉ
#  or FITNESS FOR A PARTICULAR          ni d’ADÉQUATION À UN OBJECTIF
#  PURPOSE.  See the GNU Affero         PARTICULIER. Consultez la Licence
#  General Public License for           Générale Publique GNU Affero
#  more details.                        pour plus de détails.
#
#  You should have received             Vous devriez avoir reçu une
#  a copy of the GNU Affero             copie de la Licence Générale
#  General Public License along         Publique GNU Affero avec
#  with OpenCADC.  If not, see          OpenCADC ; si ce n’est
#  <http://www.gnu.org/licenses/>.      pas le cas, consultez :
#                                       <http://www.gnu.org/licenses/>.
#
#  $Revision: 4 $
#
#***********************************************************************
#

""" Defines TestCoordAxis1D class """

import unittest

from caom2.wcs.caom2_axis import Axis
from caom2.wcs.caom2_coord_axis1d import CoordAxis1D
from caom2.wcs.caom2_coord_bounds1d import CoordBounds1D
from caom2.wcs.caom2_coord_error import CoordError
from caom2.wcs.caom2_coord_function1d import CoordFunction1D
from caom2.wcs.caom2_coord_range1d import CoordRange1D
from caom2.wcs.caom2_ref_coord import RefCoord


class TestCoordAxis1D(unittest.TestCase):

    def testInit(self):

        self.assertRaises(TypeError, CoordAxis1D, None)
        self.assertRaises(TypeError, CoordAxis1D, int(1))

        axis = Axis("ctype", "cunit")
        axis_1d = CoordAxis1D(axis)
        self.assertEqual(axis_1d.axis, axis)
        with self.assertRaises(TypeError):
            axis_1d.error = str("s")
            axis_1d.bounds = str("s")
            axis_1d.function = str("s")
            axis_1d.range = str("s")

        error = CoordError(float(1.0), float(2.0))
        axis_1d.error = error
        self.assertEqual(axis_1d.error, error)

        start = RefCoord(float(1.0), float(2.0))
        end = RefCoord(float(3.0), float(4.0))
        coordRange = CoordRange1D(start, end)
        axis_1d.range = coordRange
        self.assertEqual(axis_1d.range, coordRange)

        bounds = CoordBounds1D()
        axis_1d.bounds = bounds
        self.assertEqual(axis_1d.bounds, bounds)

        naxis = long(1)
        delta = float(2.5)
        ref_coord = RefCoord(float(1.0), float(2.0))
        function = CoordFunction1D(naxis, delta, ref_coord)
        axis_1d.function = function
        self.assertEqual(axis_1d.function, function)


if __name__ == '__main__':
    unittest.main()

