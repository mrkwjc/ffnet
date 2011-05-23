/* ffnet.f -- translated by f2c (version 20060506).
   You must link the resulting object file with libf2c:
	on Microsoft Windows system, link with libf2c.lib;
	on Linux or Unix systems, link with .../path/to/libf2c.a -lm
	or, if you install libf2c.a in a standard place, with -lf2c -lm
	-- in that order, at the end of the command line, as in
		cc *.o -lf2c -lm
	Source for libf2c is in /netlib/f2c/libf2c.zip, e.g.,

		http://www.netlib.org/f2c/libf2c.zip
*/

#include "f2c.h"

/* Table of constant values */

static doublereal c_b8 = 0.;
static doublereal c_b9 = 1.;

/* ####################################################################### */
/* #  Copyright (C) 2006 by Marek Wojciechowski */
/* #  <mwojc@p.lodz.pl> */
/* # */
/* #  Distributed under the terms of the GNU General Public License (GPL) */
/* #  http://www.gnu.org/copyleft/gpl.html */
/* ####################################################################### */

/* c */
/* cc */
/* ccc */
/* cccc BASIC FFNN PROPAGATION ROUTINES */
/* ccc */
/* cc */
/* c */

/* ************************************************************************ */
/* Subroutine */ int prop_(doublereal *x, integer *conec, integer *n, 
	doublereal *units, integer *u)
{
    /* System generated locals */
    integer conec_dim1, conec_offset, i__1;

    /* Builtin functions */
    double exp(doublereal);

    /* Local variables */
    static integer xn, src, trg, ctrg;

/* ************************************************************************ */

/* .....Gets conec and units with input already set */
/* .....and calculates all activations. */
/* .....Identity input and sigmoid activation function for other units */
/* .....is assumed */

/* .....variables */
/* .....helper variables */
/* .....f2py statements */
/* f2py intent(in, out) units */
/* .....propagate signals with sigmoid activation function */
    /* Parameter adjustments */
    conec_dim1 = *n;
    conec_offset = 1 + conec_dim1;
    conec -= conec_offset;
    --x;
    --units;

    /* Function Body */
    if (*n > 0) {
	ctrg = conec[(conec_dim1 << 1) + 1];
	units[ctrg] = 0.f;
	i__1 = *n;
	for (xn = 1; xn <= i__1; ++xn) {
	    src = conec[xn + conec_dim1];
	    trg = conec[xn + (conec_dim1 << 1)];
/* if next unit */
	    if (trg != ctrg) {
		units[ctrg] = 1.f / (exp(-units[ctrg]) + 1.f);
		ctrg = trg;
		if (src == 0) {
/* handle bias */
		    units[ctrg] = x[xn];
		} else {
		    units[ctrg] = units[src] * x[xn];
		}
	    } else {
		if (src == 0) {
/* handle bias */
		    units[ctrg] += x[xn];
		} else {
		    units[ctrg] += units[src] * x[xn];
		}
	    }
	}
	units[ctrg] = 1.f / (exp(-units[ctrg]) + 1.f);
/* for last unit */
    }
    return 0;
} /* prop_ */

/* ************************************************************************ */
/* Subroutine */ int sqerror_(doublereal *x, integer *conec, integer *n, 
	doublereal *units, integer *u, integer *inno, integer *i__, integer *
	outno, integer *o, doublereal *input, doublereal *targ, integer *p, 
	doublereal *sqerr)
{
    /* System generated locals */
    integer conec_dim1, conec_offset, input_dim1, input_offset, targ_dim1, 
	    targ_offset, i__1, i__2;
    doublereal d__1;

    /* Local variables */
    static integer k, pat;
    extern /* Subroutine */ int prop_(doublereal *, integer *, integer *, 
	    doublereal *, integer *);

/* ************************************************************************ */

/* .....Takes Input and Target patterns and returns sum of squared errors */

/* .....variables */
/* .....helper variables */
/* .....f2py statements */
/* f2py intent(out) sqerr */
    /* Parameter adjustments */
    conec_dim1 = *n;
    conec_offset = 1 + conec_dim1;
    conec -= conec_offset;
    --x;
    --units;
    --inno;
    --outno;
    targ_dim1 = *p;
    targ_offset = 1 + targ_dim1;
    targ -= targ_offset;
    input_dim1 = *p;
    input_offset = 1 + input_dim1;
    input -= input_offset;

    /* Function Body */
    *sqerr = 0.f;
/* .....loop over given patterns */
    i__1 = *p;
    for (pat = 1; pat <= i__1; ++pat) {
/* .........set input units */
	i__2 = *i__;
	for (k = 1; k <= i__2; ++k) {
	    units[inno[k]] = input[pat + k * input_dim1];
	}
/* .........propagate signals */
	prop_(&x[1], &conec[conec_offset], n, &units[1], u);
/* .........sum squared errors */
	i__2 = *o;
	for (k = 1; k <= i__2; ++k) {
/* Computing 2nd power */
	    d__1 = units[outno[k]] - targ[pat + k * targ_dim1];
	    *sqerr += d__1 * d__1;
	}
    }
    *sqerr *= .5;
    return 0;
} /* sqerror_ */

/* ************************************************************************ */
/* Subroutine */ int grad_(doublereal *x, integer *conec, integer *n, integer 
	*bconecno, integer *bn, doublereal *units, integer *u, integer *inno, 
	integer *i__, integer *outno, integer *o, doublereal *input, 
	doublereal *targ, integer *p, doublereal *xprime)
{
    /* System generated locals */
    integer conec_dim1, conec_offset, input_dim1, input_offset, targ_dim1, 
	    targ_offset, i__1, i__2;

    /* Local variables */
    static integer k;
    static doublereal cx;
    static integer pat, src, trg;
    static doublereal diff[100000];
    static integer ctrg;
    extern /* Subroutine */ int prop_(doublereal *, integer *, integer *, 
	    doublereal *, integer *);
    static doublereal deriv, bunits[100000];

/* ************************************************************************ */

/* .....Takes conec, bconecno, Input and Target patterns and returns */
/* .....gradient calculated with error backpropagation */

/* .....variables */
/* .....helper variables */
/* .....f2py statements */
/* f2py intent(out) xprime */
/* .....initialize xprime */
    /* Parameter adjustments */
    --xprime;
    conec_dim1 = *n;
    conec_offset = 1 + conec_dim1;
    conec -= conec_offset;
    --x;
    --bconecno;
    --units;
    --inno;
    --outno;
    targ_dim1 = *p;
    targ_offset = 1 + targ_dim1;
    targ -= targ_offset;
    input_dim1 = *p;
    input_offset = 1 + input_dim1;
    input -= input_offset;

    /* Function Body */
    i__1 = *n;
    for (k = 1; k <= i__1; ++k) {
	xprime[k] = 0.f;
    }
/* .....loop over given patterns */
    i__1 = *p;
    for (pat = 1; pat <= i__1; ++pat) {
/* .........propagate input signals */
	i__2 = *i__;
	for (k = 1; k <= i__2; ++k) {
	    units[inno[k]] = input[pat + k * input_dim1];
	}
	prop_(&x[1], &conec[conec_offset], n, &units[1], u);
/* .........set diffs at network output as back network inputs */
	i__2 = *o;
	for (k = 1; k <= i__2; ++k) {
	    diff[k - 1] = units[outno[k]] - targ[pat + k * targ_dim1];
	    deriv = units[outno[k]] * (1.f - units[outno[k]]);
/* ugly */
	    bunits[outno[k] - 1] = diff[k - 1] * deriv;
	}
/* .........backpropagate errors */
	if (*bn > 0) {
	    ctrg = conec[bconecno[1] + conec_dim1];
	    bunits[ctrg - 1] = 0.f;
	    i__2 = *bn;
	    for (k = 1; k <= i__2; ++k) {
		src = conec[bconecno[k] + (conec_dim1 << 1)];
		trg = conec[bconecno[k] + conec_dim1];
		cx = x[bconecno[k]];
		if (trg != ctrg) {
/* if next unit */
		    deriv = units[ctrg] * (1.f - units[ctrg]);
/* ugly */
		    bunits[ctrg - 1] *= deriv;
		    ctrg = trg;
		    bunits[ctrg - 1] = bunits[src - 1] * cx;
		} else {
		    bunits[ctrg - 1] += bunits[src - 1] * cx;
		}
	    }
	    deriv = units[ctrg] * (1 - units[ctrg]);
	    bunits[ctrg - 1] *= deriv;
/* for last unit */
	}
/* .........add gradient elements to overall xprime */
	i__2 = *n;
	for (k = 1; k <= i__2; ++k) {
	    src = conec[k + conec_dim1];
	    trg = conec[k + (conec_dim1 << 1)];
	    if (src == 0) {
/* handle bias */
		xprime[k] += bunits[trg - 1];
	    } else {
		xprime[k] += units[src] * bunits[trg - 1];
	    }
	}
    }
    return 0;
} /* grad_ */

/* ************************************************************************ */
/* Subroutine */ int recall_(doublereal *x, integer *conec, integer *n, 
	doublereal *units, integer *u, integer *inno, integer *i__, integer *
	outno, integer *o, doublereal *input, doublereal *output)
{
    /* System generated locals */
    integer conec_dim1, conec_offset, i__1;

    /* Local variables */
    static integer k;
    extern /* Subroutine */ int prop_(doublereal *, integer *, integer *, 
	    doublereal *, integer *);

/* ************************************************************************ */

/* .....Takes single input pattern and returns network output */

/* .....variables */
/* .....helper variables */
/* .....f2py statements */
/* f2py intent(out) output */
/* .....set input units */
    /* Parameter adjustments */
    conec_dim1 = *n;
    conec_offset = 1 + conec_dim1;
    conec -= conec_offset;
    --x;
    --units;
    --input;
    --inno;
    --output;
    --outno;

    /* Function Body */
    i__1 = *i__;
    for (k = 1; k <= i__1; ++k) {
	units[inno[k]] = input[k];
    }
/* .....propagate signals */
    prop_(&x[1], &conec[conec_offset], n, &units[1], u);
/* .....get output */
    i__1 = *o;
    for (k = 1; k <= i__1; ++k) {
	output[k] = units[outno[k]];
    }
    return 0;
} /* recall_ */

/* ************************************************************************ */
/* Subroutine */ int diff_(doublereal *x, integer *conec, integer *n, integer 
	*dconecno, integer *dn, integer *dconecmk, doublereal *units, integer 
	*u, integer *inno, integer *i__, integer *outno, integer *o, 
	doublereal *input, doublereal *deriv)
{
    /* System generated locals */
    integer conec_dim1, conec_offset, deriv_dim1, deriv_offset, i__1, i__2;

    /* Local variables */
    static integer k, di;
    static doublereal dx;
    static integer xn, src, trg, ctrg;
    extern /* Subroutine */ int prop_(doublereal *, integer *, integer *, 
	    doublereal *, integer *);
    static doublereal dunits[100000];

/* ************************************************************************ */

/* .....Takes single input pattern and returns network partial derivatives */
/* .....in the form d(output,o)/d(input,i). 'units' contain now activation */
/* .....derivatives */

/* .....variables */
/* .....helper variables */
/* .....f2py statements */
/* f2py intent(out) deriv */
/* .....first set inputs for usual and derivative network units */
    /* Parameter adjustments */
    conec_dim1 = *n;
    conec_offset = 1 + conec_dim1;
    conec -= conec_offset;
    --x;
    --dconecno;
    --units;
    --input;
    --inno;
    --dconecmk;
    deriv_dim1 = *o;
    deriv_offset = 1 + deriv_dim1;
    deriv -= deriv_offset;
    --outno;

    /* Function Body */
    i__1 = *i__;
    for (k = 1; k <= i__1; ++k) {
	units[inno[k]] = input[k];
	dunits[inno[k] - 1] = 0.;
    }
/* .....calculate derivatives of activation functions --> units became */
/* .....units derivatives (ugly, usable only for sigmoid function */
/* .....and identity input) */
    prop_(&x[1], &conec[conec_offset], n, &units[1], u);
    i__1 = *u;
    for (k = 1; k <= i__1; ++k) {
	units[k] *= 1. - units[k];
    }
    i__1 = *i__;
    for (k = 1; k <= i__1; ++k) {
	units[inno[k]] = 1.;
    }
/* .....prepare output units for derivative network */
    i__1 = *o;
    for (k = 1; k <= i__1; ++k) {
	dunits[outno[k] - 1] = 0.;
    }
/* .....loop over inputs */
    i__1 = *i__;
    for (di = 1; di <= i__1; ++di) {
/* .........set current input unit derivative as network input */
	dunits[inno[di] - 1] = units[inno[di]];
/* .........propagate signals through derivative network (dunits became */
/* .........net units and units derivatives are now scaling factors) */
	if (*dn > 0) {
	    ctrg = conec[dconecno[dconecmk[di] + 1] + (conec_dim1 << 1)];
	    dunits[ctrg - 1] = 0.f;
	    i__2 = dconecmk[di + 1];
	    for (xn = dconecmk[di] + 1; xn <= i__2; ++xn) {
		src = conec[dconecno[xn] + conec_dim1];
		trg = conec[dconecno[xn] + (conec_dim1 << 1)];
		dx = x[dconecno[xn]];
		if (trg != ctrg) {
		    dunits[ctrg - 1] *= units[ctrg];
		    ctrg = trg;
		    dunits[ctrg - 1] = dunits[src - 1] * dx;
		} else {
		    dunits[ctrg - 1] += dunits[src - 1] * dx;
		}
	    }
	    dunits[ctrg - 1] *= units[ctrg];
/* for last unit */
	}
/* .........save network outputs (do/di) */
	i__2 = *o;
	for (k = 1; k <= i__2; ++k) {
	    deriv[k + di * deriv_dim1] = dunits[outno[k] - 1];
	    dunits[outno[k] - 1] = 0.;
	}
/* .........restore current input */
	dunits[inno[di] - 1] = 0.;
    }
    return 0;
} /* diff_ */


/* c */
/* cc */
/* ccc */
/* cccc EXTENSIONS OF BASIC ROUTINES */
/* ccc */
/* cc */
/* c */

/* ************************************************************************ */
/* Subroutine */ int func_(doublereal *x, integer *conec, integer *n, integer 
	*bconecno, integer *bn, doublereal *units, integer *u, integer *inno, 
	integer *i__, integer *outno, integer *o, doublereal *input, 
	doublereal *targ, integer *p, doublereal *sqerr)
{
    /* System generated locals */
    integer conec_dim1, conec_offset, input_dim1, input_offset, targ_dim1, 
	    targ_offset;

    /* Local variables */
    extern /* Subroutine */ int sqerror_(doublereal *, integer *, integer *, 
	    doublereal *, integer *, integer *, integer *, integer *, integer 
	    *, doublereal *, doublereal *, integer *, doublereal *);

/* ************************************************************************ */

/* .....Just calls sqerror, but now the agruments list */
/* .....is compatibile with grad. This compatibility is needed by scipy */
/* .....optimizers. */

/* .....variables */
/* .....f2py statements */
/* f2py intent(out) sqerr */
    /* Parameter adjustments */
    conec_dim1 = *n;
    conec_offset = 1 + conec_dim1;
    conec -= conec_offset;
    --x;
    --bconecno;
    --units;
    --inno;
    --outno;
    targ_dim1 = *p;
    targ_offset = 1 + targ_dim1;
    targ -= targ_offset;
    input_dim1 = *p;
    input_offset = 1 + input_dim1;
    input -= input_offset;

    /* Function Body */
    sqerror_(&x[1], &conec[conec_offset], n, &units[1], u, &inno[1], i__, &
	    outno[1], o, &input[input_offset], &targ[targ_offset], p, sqerr);
    return 0;
} /* func_ */

/* ************************************************************************ */
/* Subroutine */ int pikaiaff_(doublereal *x, integer *ffn, integer *conec, 
	integer *n, doublereal *units, integer *u, integer *inno, integer *
	i__, integer *outno, integer *o, doublereal *input, doublereal *targ, 
	integer *p, doublereal *bound1, doublereal *bound2, doublereal *
	isqerr)
{
    /* System generated locals */
    integer conec_dim1, conec_offset, input_dim1, input_offset, targ_dim1, 
	    targ_offset;

    /* Local variables */
    static doublereal x2[100000];
    extern /* Subroutine */ int vmapa_(doublereal *, integer *, doublereal *, 
	    doublereal *, doublereal *, doublereal *, doublereal *), sqerror_(
	    doublereal *, integer *, integer *, doublereal *, integer *, 
	    integer *, integer *, integer *, integer *, doublereal *, 
	    doublereal *, integer *, doublereal *);

/* ************************************************************************ */

/* .....Routine for use with pikaia - genetic algorithm based optimizer. */
/* .....Takes Input and Target patterns and returns inverse of */
/* .....sum of quared errors. Note: (bound1, bound2) */
/* .....is constraint range for x. */

/* .....variables */
/* .....f2py statements */
/* f2py intent(out) isqerr */
/* .....first map x vector values from 0,1 to bound1,bound2 */
    /* Parameter adjustments */
    conec_dim1 = *n;
    conec_offset = 1 + conec_dim1;
    conec -= conec_offset;
    --x;
    --units;
    --inno;
    --outno;
    targ_dim1 = *p;
    targ_offset = 1 + targ_dim1;
    targ -= targ_offset;
    input_dim1 = *p;
    input_offset = 1 + input_dim1;
    input -= input_offset;

    /* Function Body */
    vmapa_(&x[1], n, &c_b8, &c_b9, bound1, bound2, x2);
/* .....now propagate patterns and obtain error */
    sqerror_(x2, &conec[conec_offset], n, &units[1], u, &inno[1], i__, &outno[
	    1], o, &input[input_offset], &targ[targ_offset], p, isqerr);
/* .....inverse error */
    *isqerr = 1.f / *isqerr;
    return 0;
} /* pikaiaff_ */

/* ************************************************************************ */
/* Subroutine */ int normcall_(doublereal *x, integer *conec, integer *n, 
	doublereal *units, integer *u, integer *inno, integer *i__, integer *
	outno, integer *o, doublereal *eni, doublereal *deo, doublereal *
	input, doublereal *output)
{
    /* System generated locals */
    integer conec_dim1, conec_offset, eni_dim1, eni_offset, deo_dim1, 
	    deo_offset;

    /* Local variables */
    extern /* Subroutine */ int prop_(doublereal *, integer *, integer *, 
	    doublereal *, integer *), setin_(doublereal *, integer *, integer 
	    *, doublereal *, doublereal *, integer *), getout_(doublereal *, 
	    integer *, integer *, integer *, doublereal *, doublereal *);

/* ************************************************************************ */

/* .....Takes single input pattern and returns network output */
/* .....This have the same functionality as recall but now input and */
/* .....output are normalized inside the function. */
/* .....eni = [ai, bi], eno = [ao, bo] - parameters of linear mapping */

/* .....variables */
/* .....f2py statements */
/* f2py intent(out) output, istat */
/* .....set input units */
    /* Parameter adjustments */
    conec_dim1 = *n;
    conec_offset = 1 + conec_dim1;
    conec -= conec_offset;
    --x;
    --units;
    --input;
    eni_dim1 = *i__;
    eni_offset = 1 + eni_dim1;
    eni -= eni_offset;
    --inno;
    --output;
    deo_dim1 = *o;
    deo_offset = 1 + deo_dim1;
    deo -= deo_offset;
    --outno;

    /* Function Body */
    setin_(&input[1], &inno[1], i__, &eni[eni_offset], &units[1], u);
/* .....propagate signals */
    prop_(&x[1], &conec[conec_offset], n, &units[1], u);
/* .....get output */
    getout_(&units[1], u, &outno[1], o, &deo[deo_offset], &output[1]);
    return 0;
} /* normcall_ */


/* ************************************************************************ */
/* Subroutine */ int normdiff_(doublereal *x, integer *conec, integer *n, 
	integer *dconecno, integer *dn, integer *dconecmk, doublereal *units, 
	integer *u, integer *inno, integer *i__, integer *outno, integer *o, 
	doublereal *eni, doublereal *ded, doublereal *input, doublereal *
	deriv)
{
    /* System generated locals */
    integer conec_dim1, conec_offset, deriv_dim1, deriv_offset, eni_dim1, 
	    eni_offset, ded_dim1, ded_offset, i__1, i__2;

    /* Local variables */
    static integer k, di;
    static doublereal dx;
    static integer xn, src, trg, ctrg;
    extern /* Subroutine */ int prop_(doublereal *, integer *, integer *, 
	    doublereal *, integer *), setin_(doublereal *, integer *, integer 
	    *, doublereal *, doublereal *, integer *);
    static doublereal dunits[100000];

/* ************************************************************************ */

/* .....Takes single input pattern and returns network partial derivatives */
/* .....in the form d(output,o)/d(input,i). 'units' contain now activation */
/* .....derivatives */
/* .....This have the same functionality as diff but now input and */
/* .....output are normalized inside function */

/* .....Solution not very smart, whole diff routine is rewritten here... */

/* .....variables */
/* .....helper variables */
/* .....f2py statements */
/* f2py intent(out) deriv */
/* .....first set inputs for usual and derivative network units */
    /* Parameter adjustments */
    conec_dim1 = *n;
    conec_offset = 1 + conec_dim1;
    conec -= conec_offset;
    --x;
    --dconecno;
    --units;
    --input;
    eni_dim1 = *i__;
    eni_offset = 1 + eni_dim1;
    eni -= eni_offset;
    --inno;
    --dconecmk;
    deriv_dim1 = *o;
    deriv_offset = 1 + deriv_dim1;
    deriv -= deriv_offset;
    ded_dim1 = *o;
    ded_offset = 1 + ded_dim1;
    ded -= ded_offset;
    --outno;

    /* Function Body */
    setin_(&input[1], &inno[1], i__, &eni[eni_offset], &units[1], u);
/* .....propagate through network */
    prop_(&x[1], &conec[conec_offset], n, &units[1], u);
/* .....calculate derivatives of activation functions --> units became */
/* .....units derivatives (ugly, usable only for sigmoid function */
/* .....and identity input) */
    i__1 = *u;
    for (k = 1; k <= i__1; ++k) {
	units[k] *= 1. - units[k];
/* units(k) = units(k) * (1d0 - units(k)) * (1d0-2d0*units(k)) */
    }
    i__1 = *i__;
    for (k = 1; k <= i__1; ++k) {
	units[inno[k]] = 1.;
    }
/* .....prepare output units and scaling factors for derivative network */
    i__1 = *o;
    for (k = 1; k <= i__1; ++k) {
	dunits[outno[k] - 1] = 0.;
    }
/* .....loop over inputs */
    i__1 = *i__;
    for (di = 1; di <= i__1; ++di) {
/* .........set current input unit derivative as network input */
	dunits[inno[di] - 1] = units[inno[di]];
/* .........propagate signals through derivative network (dunits became */
/* .........net units and units derivatives are now scaling factors) */
	if (*dn > 0) {
	    ctrg = conec[dconecno[dconecmk[di] + 1] + (conec_dim1 << 1)];
	    dunits[ctrg - 1] = 0.f;
	    i__2 = dconecmk[di + 1];
	    for (xn = dconecmk[di] + 1; xn <= i__2; ++xn) {
		src = conec[dconecno[xn] + conec_dim1];
		trg = conec[dconecno[xn] + (conec_dim1 << 1)];
		dx = x[dconecno[xn]];
		if (trg != ctrg) {
		    dunits[ctrg - 1] *= units[ctrg];
		    ctrg = trg;
		    dunits[ctrg - 1] = dunits[src - 1] * dx;
		} else {
		    dunits[ctrg - 1] += dunits[src - 1] * dx;
		}
	    }
	    dunits[ctrg - 1] *= units[ctrg];
/* for last unit */
	}
/* .........save network outputs (do/di) */
	i__2 = *o;
	for (k = 1; k <= i__2; ++k) {
	    deriv[k + di * deriv_dim1] = dunits[outno[k] - 1] * ded[k + di * 
		    ded_dim1];
	    dunits[outno[k] - 1] = 0.;
	}
/* .........restore current input */
	dunits[inno[di] - 1] = 0.;
    }
    return 0;
} /* normdiff_ */


/* ************************************************************************ */
/* Subroutine */ int normcall2_(doublereal *x, integer *conec, integer *n, 
	doublereal *units, integer *u, integer *inno, integer *i__, integer *
	outno, integer *o, doublereal *eni, doublereal *deo, doublereal *
	input, integer *p, doublereal *output)
{
    /* System generated locals */
    integer conec_dim1, conec_offset, input_dim1, input_offset, output_dim1, 
	    output_offset, eni_dim1, eni_offset, deo_dim1, deo_offset, i__1, 
	    i__2;

    /* Local variables */
    extern /* Subroutine */ int normcall_(doublereal *, integer *, integer *, 
	    doublereal *, integer *, integer *, integer *, integer *, integer 
	    *, doublereal *, doublereal *, doublereal *, doublereal *);
    static integer j, k;
    static doublereal tmpinp[100000], tmpout[100000];

/* ************************************************************************ */

/* .....Calls normcall for an array if inputs and return array of outputs */

/* .....variables */
/* .....helper variables */
/* .....f2py statements */
/* f2py intent(out) output, istat */
/* .....iterate over input set */
    /* Parameter adjustments */
    conec_dim1 = *n;
    conec_offset = 1 + conec_dim1;
    conec -= conec_offset;
    --x;
    --units;
    eni_dim1 = *i__;
    eni_offset = 1 + eni_dim1;
    eni -= eni_offset;
    --inno;
    deo_dim1 = *o;
    deo_offset = 1 + deo_dim1;
    deo -= deo_offset;
    --outno;
    output_dim1 = *p;
    output_offset = 1 + output_dim1;
    output -= output_offset;
    input_dim1 = *p;
    input_offset = 1 + input_dim1;
    input -= input_offset;

    /* Function Body */
    i__1 = *p;
    for (j = 1; j <= i__1; ++j) {
	i__2 = *i__;
	for (k = 1; k <= i__2; ++k) {
	    tmpinp[k - 1] = input[j + k * input_dim1];
	}
	normcall_(&x[1], &conec[conec_offset], n, &units[1], u, &inno[1], i__,
		 &outno[1], o, &eni[eni_offset], &deo[deo_offset], tmpinp, 
		tmpout);
	i__2 = *o;
	for (k = 1; k <= i__2; ++k) {
	    output[j + k * output_dim1] = tmpout[k - 1];
	}
    }
    return 0;
} /* normcall2_ */


/* ************************************************************************ */
/* Subroutine */ int normdiff2_(doublereal *x, integer *conec, integer *n, 
	integer *dconecno, integer *dn, integer *dconecmk, doublereal *units, 
	integer *u, integer *inno, integer *i__, integer *outno, integer *o, 
	doublereal *eni, doublereal *ded, doublereal *input, integer *p, 
	doublereal *deriv)
{
    /* System generated locals */
    integer conec_dim1, conec_offset, input_dim1, input_offset, deriv_dim1, 
	    deriv_dim2, deriv_offset, eni_dim1, eni_offset, ded_dim1, 
	    ded_offset, i__1, i__2, i__3;

    /* Local variables */
    extern /* Subroutine */ int normdiff_(doublereal *, integer *, integer *, 
	    integer *, integer *, integer *, doublereal *, integer *, integer 
	    *, integer *, integer *, integer *, doublereal *, doublereal *, 
	    doublereal *, doublereal *);
    static integer j, k, l;
    static doublereal tmpder[1000000]	/* was [1000][1000] */, tmpinp[100000]
	    ;

/* ************************************************************************ */

/* .....Calls normdiff for an array if inputs and return array of derivs */

/* .....variables */
/* .....helper variables */
/* .....f2py statements */
/* f2py intent(out) deriv */
/* .....iterate over input set */
    /* Parameter adjustments */
    conec_dim1 = *n;
    conec_offset = 1 + conec_dim1;
    conec -= conec_offset;
    --x;
    --dconecno;
    --units;
    eni_dim1 = *i__;
    eni_offset = 1 + eni_dim1;
    eni -= eni_offset;
    --inno;
    --dconecmk;
    ded_dim1 = *o;
    ded_offset = 1 + ded_dim1;
    ded -= ded_offset;
    --outno;
    deriv_dim1 = *p;
    deriv_dim2 = *o;
    deriv_offset = 1 + deriv_dim1 * (1 + deriv_dim2);
    deriv -= deriv_offset;
    input_dim1 = *p;
    input_offset = 1 + input_dim1;
    input -= input_offset;

    /* Function Body */
    i__1 = *p;
    for (j = 1; j <= i__1; ++j) {
	i__2 = *i__;
	for (k = 1; k <= i__2; ++k) {
	    tmpinp[k - 1] = input[j + k * input_dim1];
	}
	normdiff_(&x[1], &conec[conec_offset], n, &dconecno[1], dn, &dconecmk[
		1], &units[1], u, &inno[1], i__, &outno[1], o, &eni[
		eni_offset], &ded[ded_offset], tmpinp, tmpder);
	i__2 = *o;
	for (k = 1; k <= i__2; ++k) {
	    i__3 = *i__;
	    for (l = 1; l <= i__3; ++l) {
		deriv[j + (k + l * deriv_dim2) * deriv_dim1] = tmpder[k + l * 
			1000 - 1001];
	    }
	}
    }
    return 0;
} /* normdiff2_ */


/* c */
/* cc */
/* ccc */
/* cccc BASIC TRAINING ALGORITHMS */
/* ccc */
/* cc */
/* c */

/* ************************************************************************ */
/* Subroutine */ int momentum_(doublereal *x, integer *conec, integer *n, 
	integer *bconecno, integer *bn, doublereal *units, integer *u, 
	integer *inno, integer *i__, integer *outno, integer *o, doublereal *
	input, doublereal *targ, integer *p, doublereal *eta, doublereal *
	moment, integer *maxiter)
{
    /* System generated locals */
    integer conec_dim1, conec_offset, input_dim1, input_offset, targ_dim1, 
	    targ_offset, i__1;

    /* Local variables */
    static integer j, k;
    extern /* Subroutine */ int grad_(doublereal *, integer *, integer *, 
	    integer *, integer *, doublereal *, integer *, integer *, integer 
	    *, integer *, integer *, doublereal *, doublereal *, integer *, 
	    doublereal *);
    static doublereal update, xprime[100000], update0[100000];

/* ************************************************************************ */

/* .....Standard backpropagation training with momentum */

/* .....variables */
/* .....helper variables */
/* .....f2py statements */
/* f2py intent(in, out) x */
/* .....initialize variables */
    /* Parameter adjustments */
    conec_dim1 = *n;
    conec_offset = 1 + conec_dim1;
    conec -= conec_offset;
    --x;
    --bconecno;
    --units;
    --inno;
    --outno;
    targ_dim1 = *p;
    targ_offset = 1 + targ_dim1;
    targ -= targ_offset;
    input_dim1 = *p;
    input_offset = 1 + input_dim1;
    input -= input_offset;

    /* Function Body */
    i__1 = *n;
    for (j = 1; j <= i__1; ++j) {
	update0[j - 1] = 0.;
    }
    k = 0;
/* .....update maxiter times */
    while(k < *maxiter) {
	grad_(&x[1], &conec[conec_offset], n, &bconecno[1], bn, &units[1], u, 
		&inno[1], i__, &outno[1], o, &input[input_offset], &targ[
		targ_offset], p, xprime);
	i__1 = *n;
	for (j = 1; j <= i__1; ++j) {
	    update = -(*eta) * xprime[j - 1];
	    x[j] = x[j] + update + *moment * update0[j - 1];
	    update0[j - 1] = update;
	}
	++k;
    }
    return 0;
} /* momentum_ */

/* ************************************************************************ */
/* Subroutine */ int rprop_(doublereal *x, integer *conec, integer *n, 
	integer *bconecno, integer *bn, doublereal *units, integer *u, 
	integer *inno, integer *i__, integer *outno, integer *o, doublereal *
	input, doublereal *targ, integer *p, doublereal *a, doublereal *b, 
	doublereal *mimin, doublereal *mimax, doublereal *xmi, integer *
	maxiter)
{
    /* System generated locals */
    integer conec_dim1, conec_offset, input_dim1, input_offset, targ_dim1, 
	    targ_offset, i__1;
    doublereal d__1;

    /* Builtin functions */
    double d_sign(doublereal *, doublereal *);

    /* Local variables */
    static integer j, k;
    extern /* Subroutine */ int grad_(doublereal *, integer *, integer *, 
	    integer *, integer *, doublereal *, integer *, integer *, integer 
	    *, integer *, integer *, doublereal *, doublereal *, integer *, 
	    doublereal *);
    static doublereal xprime[100000], xprime0[100000];

/* ************************************************************************ */

/* .....Rprop training algorithm */

/* .....variables */
/* .....helper variables */
/* .....f2py statements */
/* f2py intent(in, out) x, xmi */
/* .....initialize variables */
    /* Parameter adjustments */
    --xmi;
    conec_dim1 = *n;
    conec_offset = 1 + conec_dim1;
    conec -= conec_offset;
    --x;
    --bconecno;
    --units;
    --inno;
    --outno;
    targ_dim1 = *p;
    targ_offset = 1 + targ_dim1;
    targ -= targ_offset;
    input_dim1 = *p;
    input_offset = 1 + input_dim1;
    input -= input_offset;

    /* Function Body */
    i__1 = *n;
    for (j = 1; j <= i__1; ++j) {
	xprime0[j - 1] = 0.;
    }
    k = 0;
/* .....update maxiter times */
    while(k < *maxiter) {
	grad_(&x[1], &conec[conec_offset], n, &bconecno[1], bn, &units[1], u, 
		&inno[1], i__, &outno[1], o, &input[input_offset], &targ[
		targ_offset], p, xprime);
	i__1 = *n;
	for (j = 1; j <= i__1; ++j) {
/* .............find mi coefficient */
	    if (xprime[j - 1] * xprime0[j - 1] > 0.) {
/* Computing MIN */
		d__1 = *a * xmi[j];
		xmi[j] = min(d__1,*mimax);
	    } else if (xprime[j - 1] * xprime0[j - 1] < 0.) {
/* Computing MAX */
		d__1 = *b * xmi[j];
		xmi[j] = max(d__1,*mimin);
	    } else {
		xmi[j] = xmi[j];
	    }
/* .............update weights and record gradient components */
	    x[j] -= d_sign(&xmi[j], &xprime[j - 1]);
	    xprime0[j - 1] = xprime[j - 1];
	}
	++k;
    }
    return 0;
} /* rprop_ */


/* c */
/* cc */
/* ccc */
/* cccc HELPER FUNCTIONS AND ROUTINES */
/* ccc */
/* cc */
/* c */

/* ************************************************************************ */
/* Subroutine */ int setin_(doublereal *input, integer *inno, integer *i__, 
	doublereal *eni, doublereal *units, integer *u)
{
    /* System generated locals */
    integer eni_dim1, eni_offset, i__1;

    /* Local variables */
    static integer k;

/* ************************************************************************ */

/* .....normalize and set input units */

/* .....variables */
/* .....helper variables */
/* .....f2py statements */
/* f2py intent(in,out) units */
    /* Parameter adjustments */
    eni_dim1 = *i__;
    eni_offset = 1 + eni_dim1;
    eni -= eni_offset;
    --inno;
    --input;
    --units;

    /* Function Body */
    i__1 = *i__;
    for (k = 1; k <= i__1; ++k) {
	units[inno[k]] = eni[k + eni_dim1] * input[k] + eni[k + (eni_dim1 << 
		1)];
    }
    return 0;
} /* setin_ */

/* ************************************************************************ */
/* Subroutine */ int getout_(doublereal *units, integer *u, integer *outno, 
	integer *o, doublereal *deo, doublereal *output)
{
    /* System generated locals */
    integer deo_dim1, deo_offset, i__1;

    /* Local variables */
    static integer k;

/* ************************************************************************ */

/* .....get and denormalize output units */

/* .....variables */
/* .....helper variables */
/* .....f2py statements */
/* f2py intent(out) output */
    /* Parameter adjustments */
    --units;
    --output;
    deo_dim1 = *o;
    deo_offset = 1 + deo_dim1;
    deo -= deo_offset;
    --outno;

    /* Function Body */
    i__1 = *o;
    for (k = 1; k <= i__1; ++k) {
	output[k] = deo[k + deo_dim1] * units[outno[k]] + deo[k + (deo_dim1 <<
		 1)];
    }
    return 0;
} /* getout_ */

/* ************************************************************************ */
doublereal mapa_(doublereal *f, doublereal *a, doublereal *b, doublereal *c__,
	 doublereal *d__)
{
    /* System generated locals */
    doublereal ret_val;

    /* Local variables */
    static doublereal t;

/* ************************************************************************ */

/* .....Linear map of f from range (a,b) to range (c,d) */

/* .....variables */
/* .....helper variables */
/* .....map vector (no check of bounds...) */
    t = (*d__ - *c__) / (*b - *a);
    ret_val = *c__ + (*f - *a) * t;
    return ret_val;
} /* mapa_ */

/* ************************************************************************ */
doublereal dmapa_(doublereal *f, doublereal *a, doublereal *b, doublereal *
	c__, doublereal *d__)
{
    /* System generated locals */
    doublereal ret_val;

/* ************************************************************************ */

/* .....Derivative of linear map of f from range (a,b) to range (c,d) */
/* .....(silly, but made for some generality purposes...) */

/* .....variables */
/* .....map vector (no check of bounds...) */
    ret_val = (*d__ - *c__) / (*b - *a);
    return ret_val;
} /* dmapa_ */

/* ************************************************************************ */
/* Subroutine */ int vmapa_(doublereal *vin, integer *n, doublereal *a, 
	doublereal *b, doublereal *c__, doublereal *d__, doublereal *vout)
{
    /* System generated locals */
    integer i__1;

    /* Local variables */
    static integer k;
    static doublereal t;

/* ************************************************************************ */

/* .....Linear map of vector elements from range (a,b) to range (c,d) */

/* .....variables */
/* .....helper variables */
/* .....f2py statements */
/* f2py intent(out) vout */
/* .....map vector (no check of bounds...) */
    /* Parameter adjustments */
    --vout;
    --vin;

    /* Function Body */
    t = (*d__ - *c__) / (*b - *a);
    i__1 = *n;
    for (k = 1; k <= i__1; ++k) {
	vout[k] = *c__ + (vin[k] - *a) * t;
    }
    return 0;
} /* vmapa_ */

/* ************************************************************************ */
/* Subroutine */ int mmapa_(doublereal *mmin, integer *m, integer *n, 
	doublereal *a, doublereal *b, doublereal *c__, doublereal *d__, 
	doublereal *mmout)
{
    /* System generated locals */
    integer mmin_dim1, mmin_offset, mmout_dim1, mmout_offset, i__1, i__2;

    /* Local variables */
    static integer j, k;
    static doublereal t;

/* ************************************************************************ */

/* .....Linear map of matrix elements from range (a,b) to range (c,d) */

/* .....variables */
/* .....helper variables */
/* .....f2py statements */
/* f2py intent(out) mmout */
/* .....map matrix (no check of bounds...) */
    /* Parameter adjustments */
    mmout_dim1 = *m;
    mmout_offset = 1 + mmout_dim1;
    mmout -= mmout_offset;
    mmin_dim1 = *m;
    mmin_offset = 1 + mmin_dim1;
    mmin -= mmin_offset;

    /* Function Body */
    t = (*d__ - *c__) / (*b - *a);
    i__1 = *m;
    for (j = 1; j <= i__1; ++j) {
	i__2 = *n;
	for (k = 1; k <= i__2; ++k) {
	    mmout[j + k * mmout_dim1] = *c__ + (mmin[j + k * mmin_dim1] - *a) 
		    * t;
	}
    }
    return 0;
} /* mmapa_ */

