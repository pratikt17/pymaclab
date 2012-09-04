#!/usr/bin/env python
#
# Created by Pearu Peterson in Febuary 2008
#

import os

from macros import preprocess
cwd = os.path.abspath(os.path.dirname(__file__))
targetfile_py = os.path.join(cwd,'..','sympycore','arithmetic','methods.py')

template = '''\
"""
Generated arithmetic methods for numbers.

This file is generated by the src/mk_numbers_methods.py script.
See http://sympycore.googlecode.com/ for more information.

DO NOT CHANGE THIS FILE DIRECTLY!!!
"""

from .numbers import mpqc, mpf, mpq, mpc, inttypes_set, realtypes_set, complextypes_set, numbertypes_set
'''

DIV_VALUE_VALUE = '''\
_p, _q = %(LHS)s, %(RHS)s
if not _q:
    raise ZeroDivisionError(repr(%(LHS)s) + " / " + repr(%(RHS)s))
@IF_CHECK_INT(T=type(_p))
    @IF_CHECK_INT(T=type(_q))
        @FRACTION_NORMALIZE(NUMER=_p; DENOM=_q; RNUMER=_rp; RDENOM=_rq; MOD=%(MOD)s)
        %(RESULT)s = _rp if _rq == 1 else mpq((_rp, _rq))
    else:
        %(RESULT)s = _p / _q
else:
    %(RESULT)s = _p / _q
'''

#=======================================================
# Constructor macros
#=======================================================

RETURN_FRACTION = '''\
return cls((%(NUMER)s, %(DENOM)s))
'''

FRACTION_NORMALIZE = '''\
%(RNUMER)s = _x = %(NUMER)s
%(RDENOM)s = _y = %(DENOM)s
while 1:
    _x, _y = _y, _x %(MOD)s _y
    if not _y:
        break
if _x != 1:
    %(RNUMER)s //= _x
    %(RDENOM)s //= _x
'''

RETURN_FRACTION2 = '''\
@FRACTION_NORMALIZE(NUMER=%(NUMER)s; DENOM=%(DENOM)s; RNUMER=_p; RDENOM=_q; MOD=%(MOD)s)
if _q == 1:
    return _p
@RETURN_FRACTION(NUMER=_p; DENOM=_q)
'''

RETURN_COMPLEX = '''\
%(TMP)s = new(cls)
%(TMP)s.real = %(REAL)s
%(TMP)s.imag = %(IMAG)s
return %(TMP)s
'''

RETURN_COMPLEX2 = '''\
%(TMP)s = %(IMAG)s
if not %(TMP)s:
    return %(REAL)s
@RETURN_COMPLEX(REAL=%(REAL)s; IMAG=%(TMP)s)
'''

#=======================================================
# ADD macros
#=======================================================

ADD_FRACTION_INT = '''\
p, q = %(LHS)s
@RETURN_FRACTION(NUMER=p+q*(%(RHS)s); DENOM=q)
'''
ADDOP_FRACTION_FRACTION = '''\
p, q = %(LHS)s
r, s = %(RHS)s
%(TMP)s = p*s %(SIGN)s q*r
if not %(TMP)s:
    return 0
@RETURN_FRACTION2(NUMER=%(TMP)s; DENOM=q*s; MOD=%(MOD)s)
'''
ADD_FRACTION_FRACTION = '''\
@ADDOP_FRACTION_FRACTION(LHS=%(LHS)s; RHS=%(RHS)s; SIGN=+; MOD=%%)
'''

ADD_COMPLEX_REAL = '@RETURN_COMPLEX(REAL=%(LHS)s.real + %(RHS)s; IMAG=%(LHS)s.imag)\n'
ADD_COMPLEX_COMPLEX = '@RETURN_COMPLEX2(REAL=%(LHS)s.real + %(RHS)s.real; IMAG=%(LHS)s.imag + %(RHS)s.imag)\n'

#=======================================================
# SUB macros
#=======================================================

SUB_FRACTION_INT = '''\
p, q = %(LHS)s
@RETURN_FRACTION(NUMER=p-q*(%(RHS)s); DENOM=q)
'''
SUB_INT_FRACTION = '''\
p, q = %(RHS)s
@RETURN_FRACTION(NUMER=q*(%(LHS)s) - p; DENOM=q)
'''
SUB_FRACTION_FRACTION = '''\
@ADDOP_FRACTION_FRACTION(LHS=%(LHS)s; RHS=%(RHS)s; SIGN=-; MOD=%%)
'''

SUB_COMPLEX_REAL = '@RETURN_COMPLEX(REAL=%(LHS)s.real - %(RHS)s; IMAG=%(LHS)s.imag)\n'
SUB_COMPLEX_COMPLEX = '@RETURN_COMPLEX2(REAL=%(LHS)s.real - %(RHS)s.real; IMAG=%(LHS)s.imag - %(RHS)s.imag)\n'
SUB_REAL_COMPLEX = '@RETURN_COMPLEX(REAL=%(LHS)s - %(RHS)s.real; IMAG=-%(RHS)s.imag)\n'

#=======================================================
# MUL macros
#=======================================================

MUL_FRACTION_INT = '''\
p, q = %(LHS)s
@RETURN_FRACTION2(NUMER=p*%(RHS)s; DENOM=q; MOD=%(MOD)s)
'''
MUL_FRACTION_FRACTION = '''\
p, q = %(LHS)s
r, s = %(RHS)s
@RETURN_FRACTION2(NUMER=p*r; DENOM=q*s; MOD=%(MOD)s)
'''

MUL_COMPLEX_REAL = '''\
if not %(RHS)s:
    return 0
@RETURN_COMPLEX(REAL=%(LHS)s.real*%(RHS)s; IMAG=%(LHS)s.imag*%(RHS)s)
'''
MUL_COMPLEX_COMPLEX = '''\
a, b = %(LHS)s.real, %(LHS)s.imag
c, d = %(RHS)s.real, %(RHS)s.imag
@RETURN_COMPLEX2(REAL=a*c-b*d; IMAG=b*c+a*d)
'''

#=======================================================
# DIV macros
#=======================================================

DIV_FRACTION_INT = '''\
p, q = %(LHS)s
@RETURN_FRACTION2(NUMER=p; DENOM=q*%(RHS)s; MOD=%(MOD)s)
'''
DIV_FRACTION_FRACTION = '''\
p, q = %(LHS)s
r, s = %(RHS)s
@RETURN_FRACTION2(NUMER=p*s; DENOM=q*r; MOD=%(MOD)s)
'''
DIV_INT_FRACTION = '''\
p, q = %(RHS)s
@RETURN_FRACTION2(NUMER=%(LHS)s*q; DENOM=p; MOD=%(MOD)s)
'''

DIV_COMPLEX_REAL = '''\
@DIV_VALUE_VALUE(LHS=%(LHS)s.real; RHS=%(RHS)s; RESULT=re; MOD=%(MOD)s)
@DIV_VALUE_VALUE(LHS=%(LHS)s.imag; RHS=%(RHS)s; RESULT=im; MOD=%(MOD)s)
@RETURN_COMPLEX(REAL=re; IMAG=im)
'''

DIV_COMPLEX_COMPLEX = '''\
a, b = %(LHS)s.real, %(LHS)s.imag
c, d = %(RHS)s.real, %(RHS)s.imag
mag = c*c + d*d
%(TMP)s = b*c-a*d
@DIV_VALUE_VALUE(LHS=a*c+b*d; RHS=mag; RESULT=re; MOD=%(MOD)s)
if not %(TMP)s:
    return re
@DIV_VALUE_VALUE(LHS=%(TMP)s; RHS=mag; RESULT=im; MOD=%(MOD)s)
@RETURN_COMPLEX(REAL=re; IMAG=im)
'''
DIV_REAL_COMPLEX = '''\
%(TMP)s = %(LHS)s
c, d = %(RHS)s.real, %(RHS)s.imag
mag = c*c + d*d
@DIV_VALUE_VALUE(LHS=-%(TMP)s*d; RHS=mag; RESULT=im; MOD=%(MOD)s)
@DIV_VALUE_VALUE(LHS= %(TMP)s*c; RHS=mag; RESULT=re; MOD=%(MOD)s)
@RETURN_COMPLEX(REAL=re; IMAG=im)
'''

#=======================================================
# POW macros
#=======================================================

POW_FRACTION_INT = '''\
%(TMP)s = %(RHS)s
p, q = %(LHS)s
if %(TMP)s > 0:
    @RETURN_FRACTION(NUMER=p**%(TMP)s; DENOM=q**%(TMP)s)
%(TMP)s = -%(TMP)s
if p > 0:
    @RETURN_FRACTION(NUMER=q**%(TMP)s; DENOM=p**%(TMP)s)
@RETURN_FRACTION(NUMER=(-q)**%(TMP)s; DENOM=(-p)**%(TMP)s)
'''

POW_COMPLEX_INT = '''\
a, b = %(LHS)s.real, %(LHS)s.imag
n = %(RHS)s
if not a:
    case = n %% 4
    if not case:
        return b**n
    elif case == 1:
        @RETURN_COMPLEX(REAL=0; IMAG=b**n)
    elif case == 2:
        return -(b**n)
    else:
        @RETURN_COMPLEX(REAL=0; IMAG=-b**n)
ta, tb = type(a), type(b)
m = 1
if ta is mpq:
    if tb is mpq:
        m = (a[1] * b[1]) ** n
        a, b = a[0]*b[1], a[1]*b[0]
    @ELIF_CHECK_INT(T=tb)
        m = a[1] ** n
        a, b = a[0], a[1]*b
elif tb is mpq:
    @IF_CHECK_INT(T=ta)
        m = b[1] ** n
        a, b = a*b[1], b[0]
c, d = 1, 0
while 1:
    if n & 1:
        c, d = a*c-b*d, b*c+a*d
        n -= 1
        if not n:
            break
    a, b = a*a-b*b, 2*a*b
    n //= 2
if m==1:
    @RETURN_COMPLEX2(REAL=c; IMAG=d)
# c,d,m are integers
@FRACTION_NORMALIZE(NUMER=c; DENOM=m; RNUMER=re_p; RDENOM=re_q; MOD=%(MOD)s)
re = re_p if re_q==1 else mpq((re_p, re_q))
if not d:
    return re
@FRACTION_NORMALIZE(NUMER=d; DENOM=m; RNUMER=im_p; RDENOM=im_q; MOD=%(MOD)s)
if im_q==1:
    im = im_p
else:
    im = mpq((im_p, im_q))
@RETURN_COMPLEX(REAL=re; IMAG=im)
'''


def main():
    f = open(targetfile_py, 'w')
    print >> f, template
    print >> f, preprocess('''

def fraction_add(self, other, cls=mpq, inttypes_set=inttypes_set):
    t = type(other)
    @IF_CHECK_INT(T=t)
        @ADD_FRACTION_INT(LHS=self; RHS=other)
    elif t is cls:
        @ADD_FRACTION_FRACTION(LHS=self; RHS=other)
    @IF_CHECK_FLOAT(T=t)
        return self + mpf(other)
    return NotImplemented

def fraction_sub(self, other, cls=mpq, inttypes_set=inttypes_set):
    t = type(other)
    @IF_CHECK_INT(T=t)
        @SUB_FRACTION_INT(LHS=self; RHS=other)
    elif t is cls:
        @SUB_FRACTION_FRACTION(LHS=self; RHS=other)
    @IF_CHECK_FLOAT(T=t)
        return self - mpf(other)
    return NotImplemented

def fraction_rsub(self, other, cls=mpq, inttypes_set=inttypes_set):
    t = type(other)
    @IF_CHECK_INT(T=t)
        @SUB_INT_FRACTION(RHS=self; LHS=other)
    @IF_CHECK_FLOAT(T=t)
        return mpf(other) - self
    return NotImplemented

def fraction_mul(self, other, cls=mpq, inttypes_set=inttypes_set):
    t = type(other)
    if t is cls:
        @MUL_FRACTION_FRACTION(LHS=self; RHS=other; MOD=%)
    @IF_CHECK_INT(T=t)
        @MUL_FRACTION_INT(LHS=self; RHS=other; MOD=%)
    @IF_CHECK_FLOAT(T=t)
        return self * mpf(other)
    return NotImplemented

def fraction_div(self, other, cls=mpq, inttypes_set=inttypes_set):
    t = type(other)
    @IF_CHECK_INT(T=t)
        @DIV_FRACTION_INT(LHS=self; RHS=other; MOD=%)
    elif t is cls:
        @DIV_FRACTION_FRACTION(LHS=self; RHS=other; MOD=%)
    @IF_CHECK_FLOAT(T=t)
        return self / mpf(other)
    return NotImplemented

def fraction_rdiv(self, other, cls=mpq, inttypes_set=inttypes_set):
    t = type(other)
    @IF_CHECK_INT(T=t)
        @DIV_INT_FRACTION(RHS=self; LHS=other; MOD=%)
    @IF_CHECK_FLOAT(T=t)
        return mpf(other) / self
    return NotImplemented

def fraction_pow(self, other, m=None, cls=mpq, inttypes_set=inttypes_set):
    t = type(other)
    @IF_CHECK_INT(T=t)
        if not other:
            return 1
        if other==1:
            return self
        @POW_FRACTION_INT(LHS=self; RHS=other)
    @IF_CHECK_FLOAT(T=t)
        return self ** mpf(other)
    return NotImplemented

def complex_add(self, other, new=object.__new__, cls=mpqc, realtypes_set=realtypes_set, complextypes_set=complextypes_set):
    t = type(other)
    @IF_CHECK_REAL(T=t)
        @ADD_COMPLEX_REAL(LHS=self; RHS=other)
    @IF_CHECK_COMPLEX(T=t)
        @ADD_COMPLEX_COMPLEX(LHS=self; RHS=other)
    return NotImplemented

def complex_sub(self, other, new=object.__new__, cls=mpqc, realtypes_set=realtypes_set, complextypes_set=complextypes_set):
    t = type(other)
    @IF_CHECK_REAL(T=t)
        @SUB_COMPLEX_REAL(LHS=self; RHS=other)
    @IF_CHECK_COMPLEX(T=t)
        @SUB_COMPLEX_COMPLEX(LHS=self; RHS=other)
    return NotImplemented

def complex_rsub(self, other, new=object.__new__, cls=mpqc, realtypes_set=realtypes_set):
    t = type(other)
    @IF_CHECK_REAL(T=t)
        @SUB_REAL_COMPLEX(LHS=other; RHS=self)
    if t is complex:
        @SUB_COMPLEX_COMPLEX(LHS=other; RHS=self)
    return NotImplemented

def complex_mul(self, other, new=object.__new__, cls=mpqc, realtypes_set=realtypes_set, complextypes_set=complextypes_set):
    t = type(other)
    @IF_CHECK_COMPLEX(T=t)
        @MUL_COMPLEX_COMPLEX(LHS=self; RHS=other)
    @IF_CHECK_REAL(T=t)
        @MUL_COMPLEX_REAL(LHS=self; RHS=other)
    return NotImplemented

def complex_div(self, other, new=object.__new__, cls=mpqc, realtypes_set=realtypes_set, complextypes_set=complextypes_set):
    t = type(other)
    @IF_CHECK_REAL(T=t)
        @DIV_COMPLEX_REAL(LHS=self; RHS=other; MOD=%)
    @IF_CHECK_COMPLEX(T=t)
        @DIV_COMPLEX_COMPLEX(LHS=self; RHS=other; MOD=%)
    return NotImplemented

def complex_rdiv(self, other, new=object.__new__, cls=mpqc, realtypes_set=realtypes_set):
    t = type(other)
    @IF_CHECK_REAL(T=t)
        @DIV_REAL_COMPLEX(LHS=other; RHS=self; MOD=%)
    if t is complex:
        @DIV_COMPLEX_COMPLEX(LHS=other; RHS=self; MOD=%)
    return NotImplemented

def complex_pow(self, other, m=None, new=object.__new__, cls=mpqc, inttypes_set=inttypes_set):
    t = type(other)
    @IF_CHECK_INT(T=t)
        if not other:
            return 1
        if other==1:
            return self
        if other==2:
            return self*self
        if other < 0:
            base, exponent = 1/self, -other
        else:
            base, exponent = self, other
        @POW_COMPLEX_INT(LHS=base; RHS=exponent; MOD=%)
    return NotImplemented
    ''', globals())

    for (n,s) in [('lt','<'), ('le','<='), ('gt','>'), ('ge','>=')]:
        print >> f, preprocess('''\
def fraction_%s(self, other, cls=mpq, inttypes_set=inttypes_set):
    p, q = self
    t = type(other)
    @IF_CHECK_INT(T=t)
        return (p %s q*other)
    elif t is cls:
        r, s = other
        return p*s %s q*r
    return NotImplemented
    ''' % (n, s, s), globals())

    f.close()


if __name__=='__main__':
    main()
