/*
 ***********************************************************************
 *  Copyright (C) 2006 by Marek Wojciechowski
 *  <mwojc@p.lodz.pl>
 *
 *  Copyright (C) 2009 by Juhani Simola
 *  <ojs@iki.fi>
 *
 *  Distributed under the terms of the GNU General Public License (GPL)
 *  http://www.gnu.org/copyleft/gpl.html
 ***********************************************************************
 */

package org.ffnet;

/**
 * Basic Feed Forward Neural Network functionality.
 */
public class FFNet {
    /** Network weights */
    private final double[] weights;
    /** Connection array */
    private final int[][] conec;
    /** List of input nodes */
    private final int[] inno;
    /** List of output nodes */
    private final int[] outno;
    /** Input normalization parameters */
    private final double[][] eni;
    /** Output denormalization parameters */
    private final double[][] deo;
    /** Network size */
    private final int unitCount;

    private static int findMax2d(int[][] table) {
        int max = Integer.MIN_VALUE;
        for (int[] row : table)
            for (int value : row)
                if (value > max)
                    max = value;
        return max;
    }

    /**
     * Sigmoid transfer function
     */
    public static double sigmoid(double x) {
        return 1 / (1 + Math.exp(-x));
    }

    public FFNet(double[] weights, int[][] conec, int[] inno, int[] outno, double[][] eni, double[][] deo) {
        assert weights.length == conec.length;
        int prev_target = conec[0][1];
        // Check that connections are properly ordered
        for (int[] connection: conec) {
            assert connection.length == 2;
            int target = connection[1];
            assert target >= prev_target;
            prev_target = target;
        }
        assert eni.length == inno.length;
        assert eni[0].length == 2;
        assert deo.length == outno.length;
        assert deo[0].length == 2;

        this.weights = weights;
        this.conec = conec;
        this.inno = inno;
        this.outno = outno;
        this.eni = eni;
        this.deo = deo;

        this.unitCount = findMax2d(conec) + 1;
    }

    /**
     * Normalizes inputs and sets network status for propagation.
     * 
     * @param input
     * @return units - network state before propagation
     */
    public double[] setInput(double[] input) {
        double[] units = new double[unitCount];

        for (int k = 0; k < inno.length; k++)
            units[inno[k]] = eni[k][0] * input[k] + eni[k][1];

        return units;
    }

    /**
     * Gets network state with input already set and calculates all activations.
     * Identity input and sigmoid activation function for other units is assumed.
     */
    public void prop(double[] units) {
        assert units.length == unitCount;

        /* Connections are arranged so, that inputs to one node are computed together */
        int ctrg = conec[0][1];
        for (int i = 0; i < conec.length; i++) {
            int src = conec[i][0];
            int trg = conec[i][1];

            // If next target, apply sigmoid
            if (trg != ctrg) {
                units[ctrg] = sigmoid(units[ctrg]);
                ctrg = trg;
                units[ctrg] = 0;
            }
            if (src == -1) // bias
                units[ctrg] += weights[i];
            else
                units[ctrg] += units[src] * weights[i];
        }
        assert ctrg != -1;
        units[ctrg] = sigmoid(units[ctrg]);
    }

    /**
     * Gets output from network state and denormalizes it
     */
    public double[] getOutput(double[] units) {
        double[] output = new double[outno.length];

        for (int k = 0; k < outno.length; k++)
            output[k] = deo[k][0] * units[outno[k]] + deo[k][1];

        return output;
    }

    /**
     * Calls the network
     * 
     * @param input Input vector
     * @return Output vector
     */
    public double[] call(double[] input) {
        assert input.length == inno.length;

        double[] units = setInput(input);
        prop(units);
        return getOutput(units);
    }
}
