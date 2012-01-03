########################################################################
##  Copyright (C) 2006 by Marek Wojciechowski
##  <mwojc@p.lodz.pl>
##
##  Distributed under the terms of the GNU General Public License (GPL)
##  http://www.gnu.org/copyleft/gpl.html
########################################################################
"""
---------------------------------
Genetic algorithm based optimizer
---------------------------------
"""

# import raw module
from fortran import _pikaia

# Wrap main pikaia routine
def pikaia (ff, n, ff_extra_args = (), \
            individuals = 100, \
            generations = 500, \
            digits = 6, \
            crossover = 0.85, \
            mutation = 2, \
            initrate = 0.005, \
            minrate = 0.0005, \
            maxrate = 0.25, \
            fitnessdiff = 1.0, \
            reproduction = 3, \
            elitism = 0, \
            verbosity = 0):

    """
    Pikaia version 1.2 - genetic algorithm based optimizer.

    Simplest usage::

        from pikaia import pikaia
        x = pikaia(ff, n)

    :Parameters:
        ff : callable
            Scalar function of the signature ff(x, [n, args]),
            where *x* is a real array of length *n* and *args*
            are extra parameters. Pikaia optimizer assumes *x*
            elements are bounded to the interval (0, 1), thus
            *ff* have to aware of this, ie. probably you need
            some internal scaling inside *ff*.

            By convention, ff should return higher values for more
            optimal parameter values (i.e., individuals which are
            more "fit"). For example, in fitting a function
            through data points, *ff* could return the inverse of
            chi**2.
        n : int
            Length of *x*. Note that you do not need
            starting point.
        ff_extra_args: tuple
            Extra arguments passed to *ff*.
        individuals : int
            Number of individuals in a population (default is 100)
        generations : int
            Number of generations over which solution is
            to evolve (default is 500)
        digits :  int
            Number of significant digits (i.e., number of
            genes) retained in chromosomal encoding (default
            is 6). (Note: This number is limited by the
            machine floating point precision. Most 32-bit
            floating point representations have only 6 full
            digits of precision. To achieve greater precision
            this routine could be converted to double
            precision, but note that this would also require
            a double precision random number generator, which
            likely would not have more than 9 digits of
            precision if it used 4-byte integers internally.)
        crossover :  float
            Crossover probability; must be  <= 1.0 (default
            is 0.85). If crossover takes place, either one
            or two splicing points are used, with equal
            probabilities.
        mutation : {1, 2, 3, 4, 5, 6}
            =====   =====================================================
            digit   description
            =====   =====================================================
              1     one-point mutation, fixed rate
              2     one-point, adjustable rate based on fitness (default)
              3     one-point, adjustable rate based on distance
              4     one-point+creep, fixed rate
              5     one-point+creep, adjustable rate based on fitness
              6     one-point+creep, adjustable rate based on distance
            =====   =====================================================
        initrate : float
            Initial mutation rate. Should be small (default
            is 0.005) (Note: the mutation rate is the probability
            that any one gene locus will mutate in any one generation.)
        minrate : float
            Minimum mutation rate. Must be >= 0.0 (default is 0.0005)
        maxrate : float
            Maximum mutation rate. Must be <= 1.0 (default is 0.25)
        fitnessdiff : float
            Relative fitness differential. Range from 0 (none)
            to 1 (maximum) (default is 1).
        reproduction : {1, 2, 3}
            Reproduction plan; 1/2/3 = Full generationalreplacement/Steady-
            state-replace-random/Steady-state-replace-worst (default is 3)
        elitism : {0, 1}
            Elitism flag; 0/1=off/on (default is 0)
            (Applies only to reproduction plans 1 and 2)
        verbosity : {0, 1, 2}
            Printed output 0/1/2=None/Minimal/Verbose (default is 0)

    :Returns:
        x : array (float32)
            The 'fittest' (optimal) solution found, i.e., the solution
            which maximizes fitness function *ff*.

    :Examples:
        >>> from pikaia import pikaia
        >>> def ff(x): return -sum(x**2)
        >>> pikaia(ff, 4, individuals=50, generations=200)
        array([  1.23000005e-04,   7.69999970e-05,   2.99999992e-05,
         2.80000004e-05], dtype=float32)

    .. note::
        Original fortran code of pikaia is written by:
        Paul Charbonneau & Barry Knapp (paulchar@hao.ucar.edu,
        knapp@hao.ucar.edu)

        Wrapped with f2py by Marek Wojciechowski (mwojc@p.lodz.pl)
    """

    # Initialize pikaia random number generator
    from random import randint
    _pikaia.rninit(randint(1, 999999999))
    del randint

    # Restore control array
    ctrl = [ individuals, generations, digits, crossover, mutation, initrate, \
             minrate, maxrate, fitnessdiff, reproduction, elitism, verbosity ]

    # Optimize
    x, f, status = _pikaia.pikaia(ff, n, ctrl, ff_extra_args)
    return x

def test():
    x = pikaia(_pikaia.twod, 2)
    print "Solution for twod:"
    print x

