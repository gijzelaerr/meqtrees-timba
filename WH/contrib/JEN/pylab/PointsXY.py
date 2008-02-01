#!/usr/bin/env python

# file: ../contrib/JEN/pylab/PointsXY.py

# Author: J.E.Noordam
# 
# Short description:
#   Class that holds a set of 2D points, for (pylab) plotting 
#
# History:
#    - 27 jan 2008: creation
#
# Remarks:
#
# Description:
#

#-------------------------------------------------------------------------------

#
#% $Id$ 
#
#
# Copyright (C) 2002-2007
# The MeqTree Foundation & 
# ASTRON (Netherlands Foundation for Research in Astronomy)
# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>,
# or write to the Free Software Foundation, Inc., 
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import pylab
import copy
import random

import PlotStyle



#======================================================================================

class PointsXY (object):
    """Encapsulation of a set of 2D points, for (pylab) plotting
    """

    def __init__(self, yy=[0], name=None, xx=None,
                 annot=None, annotpos='auto',
                 plotmode='pylab',
                 **kwargs):

        #------------------------------------------------------------------

        # Deal with the specified name (label):
        self._name = name
        if not isinstance(self._name,str): self._name = '<name>'

        #------------------------------------------------------------------

        # The PlotStyle specifications are via the kwargs
        self._plotmode = plotmode
        self._PlotStyle = PlotStyle.PlotStyle(**kwargs)
        print '** init:',self._PlotStyle.oneliner()
        # self.check_PlotStyle(**kwargs)

        #------------------------------------------------------------------

        # print '\n** yy=',yy,type(yy),isinstance(yy, type(pylab.array([0]))),'\n'

        # Deal with the specified y-coordinates:
        is_complex = False
        if isinstance(yy, (list,tuple)):
            for y in yy:
                if isinstance(y, complex): is_complex = True
            self._yy = pylab.array(yy)
        elif isinstance(yy, type(pylab.array([0]))):
            for y in yy.tolist():
                if isinstance(y, complex): is_complex = True
            self._yy = yy
        else:
            self._yy = pylab.array([yy])
            is_complex = isinstance(yy, complex)

        # If yy is complex, use the real and imag parts as xx and yy:
        if is_complex:
            self._xx = self._yy.real
            self._yy = self._yy.imag

        # Deal with the specified x-coordinates (if any):
        elif xx==None:                                  # xx not specified: automatic
            # self._xx = range(self.len())            # start at x=0
            self._xx = range(1,1+self.len())          # start at x=1
            self._xx = pylab.array(self._xx)
            self._xunit = None
        elif isinstance(xx, (list,tuple)):
            self._xx = pylab.array(xx)
        elif isinstance(xx, type(pylab.array([0]))):
            self._xx = xx
        else:
            self._xx = pylab.array([xx])

        if not len(self._xx)==self.len():             # xx and yy should have the same length
            s = 'length mismatch between nyy='+str(self.len())+' and nxx='+str(len(self._xx))
            raise ValueError,s


        #------------------------------------------------------------------

        # Deal with point annotations (optional):
        self._annot = annot
        self._annotpos = annotpos
        if not self._annot==None:
            if isinstance(self._annot, (str,int,float)):
                self._annot = [self._annot]
            if not isinstance(self._annot, list):
                s = 'annot should be a list, but is: '+str(type(self._annot))
                raise ValueError,s
            elif not len(self._annot) in [1,self.len()]:
                s = 'length mismatch between nyy='+str(self.len())+' and nannot='+str(len(self._annot))
                raise ValueError,s
            else:
                for i,s in enumerate(self._annot):
                    if not isinstance(s,str):
                        self._annot[i] = str(s)

        #------------------------------------------------------------------

        # Finished:
        return None


    #===============================================================
    # Access routines:
    #===============================================================

    def len(self):
        """Return the length (nr of points)"""
        return len(self._yy)

    def name(self):
        """Return the name (label?) of this set of points"""
        return self._name

    #------------------------------------------------

    def yy(self, tolist=False):
        """Return the y-coordinate(s).
        If new is specified, replace them."""
        if tolist: return self._yy.tolist()
        return self._yy

    def yrange(self, margin=0.0, yrange=None):
        """Return [min,max] of the y-coordinate(s)."""
        return self._range(self.yy(), margin=margin, vrange=yrange)

    def __getitem__(self, index):
        """Return the coordinates [x,y] of the specified (index) point"""
        return [self._xx.tolist()[index],self._yy.tolist()[index]]

    def mean(self, mode='y'):
        """Return the mean of the specified coordinates:
        - mode=y: -> mean(yy) (default)
        - mode=x: -> mean(xx)
        - mode=r: -> sqrt(mean(xx)**2+mean(yy)**2)
        - mode=xy: -> [mean(xx),mean(yy)]"""
        if mode=='y': return pylab.mean(self._yy)
        if mode=='xy': return [pylab.mean(self._xx),pylab.mean(self._yy)]
        if mode=='r': return (pylab.mean(self._xx)**2+pylab.mean(self._yy)**2)**0.5
        if mode=='x': return pylab.mean(self._xx)
        return None

    def stddev(self, mode='y'):
        """Return the stddev of the specified coordinates:
        - mode=y: -> stddev(yy) (default)
        - mode=x: -> stddev(xx)
        - mode=xy: -> [stddev(xx),stddev(yy)]"""
        if self.len()==1:
            if mode=='xy': return [0.0,0.0]
            return 0.0
        if mode=='y': return self._yy.stddev()
        if mode=='xy': return [self._xx.stddev(),self._yy.stddev()]
        if mode=='x': return self._xx.stddev()
        return None


    #------------------------------------------------

    def xx(self, tolist=False):
        """Return the x-coordinate(s)"""
        if tolist: return self._yy.tolist()
        return self._xx

    def xrange(self, margin=0.0, xrange=None):
        """Return [min,max] of the x-coordinate(s)."""
        return self._range(self.xx(), margin=margin, vrange=xrange)

    #------------------------------------------------

    def _range(self, vv, margin=0.0, vrange=None):
        """Return [min,max] of the y-coordinate(s).
        An extra margin (fraction of the span) may be specified.
        If an existing range [min,max] is specified, take it into account."""
        vmin = min(vv)
        vmax = max(vv)
        if margin>0.0:
            dv2 = 0.5*(vmax-vmin)*margin
            if vmax==vmin:
                dv2 = 0.0004
                if not vmax==0.0:
                    dv2 *= vmax
            vmin -= dv2
            vmax += dv2
        if isinstance(vrange,(list,tuple)):
            vmin = min(vrange[0],vmin)
            vmax = max(vrange[1],vmax)
        return [vmin,vmax]


    #===============================================================
    # Display of the contents of this object:
    #===============================================================

    def oneliner(self):
        """Return a one-line summary of this object"""
        ss = '** <PointsXY> '+self.name()+':'
        ss += ' n='+str(self.len())
        ss += ' '+self._PlotStyle.summary()
        ss += '  yrange='+str(self.yrange())
        ss += '  xrange='+str(self.xrange())
        return ss


    #===============================================================
    # Modifying operations on the group of points
    #===============================================================

    def shift(self, dy=0.0, dx=0.0):
        """Shift all points by the specified dx and/or dy"""
        if isinstance(dy,complex):
            dx = real(dy)
            dy = imag(dy)
        if not dy==0.0:
            self._yy += dy
        if not dx==0.0:
            self._xx += dx
        return [dx,dy]

    def rotate(self, angle=0.0, xy0=[0.0,0.0]):
        """Rotate all points by the specified angle (rad),
        around the specified centre xy0=[x0,y0].
        If xy0 is complex, the real and imag parts are used."""
        print '** .rotate(',angle,xy0,'):'
        if not angle==0.0:
            # Make xy0 the origin:
            if isinstance(xy0,complex):
                x0 = real(xy0)
                y0 = imag(xy0)
            else:
                x0 = xy0[0]
                y0 = xy0[1]
            print 'x0=',x0,'  y0=',y0
            xx = self._xx - x0
            yy = self._yy - y0
            # Rotate around the origin:
            sina = pylab.sin(angle)
            cosa = pylab.cos(angle)
            self._xx = xx*cosa - yy*sina
            self._yy = xx*sina + yy*cosa
            # Return to the original origin:
            self._xx += x0
            self._yy += y0
        return False


    #===============================================================
    # Plot:
    #===============================================================

    def plot(self, margin=0.2, dispose='show',
             plot_mean=False, plot_stddev=False):
        """Plot the group of points, using pylab"""
        pylab.plot(self.xx(), self.yy(), **self._PlotStyle.kwargs('plot'))
        if margin>0.0:
            [xmin,xmax] = self.xrange(margin=margin)
            [ymin,ymax] = self.yrange(margin=margin)
            pylab.axis([xmin, xmax, ymin, ymax])

        # Optional extras:
        color = self._PlotStyle.color()
        if plot_mean:
            self.plot_ellipse(x0=0.0, y0=0.0, a=self.mean('r'),
                              color=color, linestyle='--')
        if plot_stddev:
            [xmean,ymean] = self.mean('xy')
            [xstddev,ystddev] = self.stddev('xy')
            self.plot_ellipse(x0=xmean, y0=ymean, a=xstddev, b=ystddev,
                              color=color, linestyle='--')
            pylab.plot([xmean], [ymean], marker='+',
                       markeredgecolor=color, markersize=20)
            pylab.plot([xmean], [ymean], marker='o',
                       markeredgecolor=color, markerfacecolor=color)
        if dispose=='show':
            pylab.show()
        return True


    #---------------------------------------------------------------

    def plot_ellipse(self, x0=0.0, y0=0.0, a=1.0, b=None,
                     color='red', linestyle='--'):
        """Make an ellipse with given centre(x0,y0) and half-axes a and b.
        If b==None (default), make a circle with radius a."""
        print x0,y0,a,b,color,linestyle
        xx = []
        yy = []
        if b==None: b = a                 # circle 
        na = 30
        angles = 2*pylab.pi*pylab.array(range(na))/float(na-1)
        for angle in angles:
            xx.append(x0+a*pylab.cos(angle))
            yy.append(y0+b*pylab.sin(angle))
        pylab.plot(xx, yy, color=color, linestyle=linestyle)
        return True


#========================================================================
# Some test objects:
#========================================================================


def test_line (n=6, name='test_line', **kwargs):
    """PointsXY object for a straight line"""
    kwargs.setdefault('color','magenta')
    kwargs.setdefault('style','o')
    yy = 0.3*pylab.array(range(n))
    pts = PointsXY (yy, name, **kwargs)
    print pts.oneliner()
    return pts

def test_parabola (n=6, name='test_parabola', **kwargs):
    """PointsXY object for a parabola"""
    kwargs.setdefault('color','blue')
    kwargs.setdefault('style','-')
    kwargs.setdefault('marker','+')
    kwargs.setdefault('markersize',10)
    yy = pylab.array(range(n))/2.0
    yy = -3+yy+yy*yy
    pts = PointsXY (yy, name, **kwargs)
    print pts.oneliner()
    return pts

def test_sine (n=10, name='test_sine', **kwargs):
    """PointsXY object for a sine-wave"""
    kwargs.setdefault('color','red')
    kwargs.setdefault('style','--')
    yy = 0.6*pylab.array(range(n))
    yy = pylab.sin(yy)
    pts = PointsXY (yy, name, **kwargs)
    print pts.oneliner()
    return pts

def test_cloud (n=10, mean=1.0, stddev=1.0, name='test_cloud', **kwargs):
    """PointsXY object for a cloud of random points"""
    kwargs.setdefault('color','green')
    kwargs.setdefault('style','cross')
    # kwargs.setdefault('markersize',10)
    yy = range(n)
    xx = range(n)
    for i,v in enumerate(yy):
        yy[i] = random.gauss(mean,stddev)
        xx[i] = random.gauss(mean,stddev)
        print '-',i,mean,stddev,':',xx[i],yy[i]
    pts = PointsXY (yy, name, xx=xx, **kwargs)
    print pts.oneliner()
    return pts


#========================================================================
# Test routine:
#========================================================================


if __name__ == '__main__':
    print '\n*******************\n** Local test of: PointsXY.py:\n'

    ps = dict()
    ps = dict(color='magenta', style='o', markersize=5, markeredgecolor='blue')

    pts = PointsXY(range(6), 'list', annot=4, **ps)
    # pts = PointsXY(pylab.array(range(6)), 'numarray', **ps)
    # pts = PointsXY(-2, 'scalar', **ps)
    # pts = PointsXY(3+5j, 'complex scalar', **ps)
    # pts = PointsXY([3,-2+1.5j], 'complex list', **ps)
    # pts = PointsXY([0,0,0,0], 'zeroes', **ps)
    # pts = test_line()
    # pts = test_sine()
    # pts = test_parabola()
    # pts = test_cloud()
    print pts.oneliner()

    if 1:
        print '- pts[1] -> ',pts[1]
        print '- pts[2] -> ',pts[2]
        print '- .yy() -> ',pts.yy(),type(pts.yy())
        print '- .yy(tolist=True) -> ',pts.yy(tolist=True),type(pts.yy(tolist=True))
        print '- .yrange(margin=0.1) -> ',pts.yrange(margin=0.1)
        print '- .xrange(margin=0.1, xrange=[-2,3]) -> ',pts.xrange(margin=0.1, xrange=[-2,3])
        print '- .mean() -> ',pts.mean()
        print '- .mean(xy) -> ',pts.mean('xy')
        print '- .mean(x) -> ',pts.mean('x')
        print '- .mean(r) -> ',pts.mean('r')
        print '- .mean(z) -> ',pts.mean('z')
        print '- .stddev() -> ',pts.stddev()
        print '- .stddev(xy) -> ',pts.stddev('xy')
        print '- .stddev(x) -> ',pts.stddev('x')

    if 0:
        print '- .shift(dy=-10, dx=100) -> ',pts.shift(dy=-10, dx=100), pts.oneliner()
        print '- .rotate(angle=0.2) -> ',pts.rotate(angle=0.2), pts.oneliner()
        print '- .rotate(angle=0.2, xy0=[-10,100]) -> ',pts.rotate(angle=0.2, xy0=[-10,100]), pts.oneliner()

    if 1:
        pts.plot(plot_mean=True, plot_stddev=True)


    print '\n** End of local test of: PointsXY.py:\n'



#-------------------------------------------------------------------------------
# Remarks:

#-------------------------------------------------------------------------------


