# Data Appendix: Induction Motor Condition Monitoring

## Introduction: Understanding This Data Appendix

The structure of this data appendix is organized as follows. Variables are grouped by their physical domain: **Current** and **Rotational Speed (RPM)**.

For each variable, we provide:
1.  A clear **definition**.
2.  **Overall summary statistics** calculated across the entire population of measurements.
3.  **Overall distribution visualizations** (histograms and/or density plots).
4.  **Summary statistics broken down by each motor condition type**:
    * Healthy - refrenced as `Healthy` on the plots
    * Mechanically Damaged - refrenced as `Mech Damage` on the plots
    * Electrically Damaged - refrenced as `Elec Damage` on the plots
    * Mechanically and Electrically Damaged refrenced as `Mech Elec Damage` on the plots
5.  **Comparative distribution visualizations** (e.g., box plots or overlaid density plots) across these motor conditions.

The data for analysis primarily consists of features extracted from measurement segments. For time-based signals (like current), the raw sensor data from the motor run is processed. After the motor reaches a **steady state** (operational equilibrium), the signal is segmented into 0.8-second intervals. The variables described in this appendix (e.g., mean, standard deviation, spectral components) are calculated from these 0.8-second samples. Time series plots may represent these sample-derived features over the sequence of samples or, in some contexts, could refer to aggregated views of longer operational periods.

All generated tables (in `.csv` format) and figures (in `.png` format) referenced below can be found in the `Output/DataAppendixOutput/` directory.

---

## I. CURRENT Domain

Current measurements are fundamental to understanding the electrical behavior and health of the induction motors. All current-related variables are measured in **Amperes (A)** unless otherwise specified.

![Current over time in example experiment per motor](../../Output/DataAppendixOutput/plot_current_whole_experiment.png)
![Current over time in example sample per motor](../../Output/DataAppendixOutput/plot_current_sample.png)

Overall statistics from CURRENT domain for whole population:

|                              |  count  |    mean     |    std    |     min     |     25%     |     50%     |     75%     |     max     |
|:----------------------------:|:-------:|:-----------:|:---------:|:-----------:|:-----------:|:-----------:|:-----------:|:-----------:|
|       CURRENT (A) mean       |   184   |   3.6953    | 0.564023  |   3.04264   |   3.15615   |   3.58206   |   4.21845   |   4.90017   |
|       CURRENT (A) std        |   184   |  0.974948   |  0.02816  |  0.888497   |  0.960363   |  0.979152   |  0.995601   |   1.02608   |
|       CURRENT (A) max        |   184   |   6.86261   | 0.529765  |   6.11673   |   6.37186   |   6.85832   |   7.29564   |   8.16266   |
|       CURRENT (A) rms        |   184   |   3.82486   | 0.543072  |   3.20063   |   3.30683   |   3.71381   |   4.31689   |   5.00265   |
|   CURRENT (A) peak_to_peak   |   184   |   6.3115    |  0.28815  |   5.7081    |   6.08224   |   6.29038   |   6.50767   |   7.18394   |
|       CURRENT (A) skew       |   184   |  0.0335438  | 0.0284482 | -0.0413872  |  0.0121713  |  0.0331058  |  0.0517989  |  0.103741   |
|     CURRENT (A) kurtosis     |   184   |  -0.355977  | 0.0365701 |  -0.420982  |  -0.386912  |  -0.360477  |  -0.327337  |  -0.265615  |
|   CURRENT (A) crest_factor   |   184   |   1.87929   |  0.15259  |   1.64775   |   1.72999   |   1.87743   |   2.02035   |   2.15757   |
| CURRENT (A) Frequency Center |   184   |   3250.88   |  450.342  |   2698.04   |   2801.81   |   3281.06   |   3692.67   |   3862.77   |
|  CURRENT (A) Spectrum Area   |   184   | 1.33527e+06 |  102617   | 1.01286e+06 | 1.29256e+06 | 1.35055e+06 | 1.41332e+06 | 1.47921e+06 |
|   CURRENT (A) Amp @ 1x RPM   |   184   |   839.349   |  625.576  |   57.4394   |   428.017   |   666.659   |   1122.42   |   3837.05   |
|   CURRENT (A) Amp @ 2x RPM   |   184   |   738.266   |  619.812  |   24.9679   |   281.279   |   493.083   |   1074.37   |   3276.88   |
|   CURRENT (A) Amp @ 3x RPM   |   184   |   687.582   |  542.484  |   17.6981   |   299.506   |   522.762   |   934.907   |   2757.53   |

Statistics from motor without damages:

|                              |  count  |    mean    |    std    |     min     |     25%     |     50%     |     75%     |     max     |
|:----------------------------:|:-------:|:----------:|:---------:|:-----------:|:-----------:|:-----------:|:-----------:|:-----------:|
|       CURRENT (A) mean       |   46    |  3.14559   | 0.0440427 |   3.04264   |   3.11298   |   3.15468   |   3.17736   |   3.24173   |
|       CURRENT (A) std        |   46    |  0.99225   | 0.0137461 |  0.957534   |  0.984792   |  0.994275   |  0.999127   |   1.01804   |
|       CURRENT (A) max        |   46    |  6.37422   | 0.146794  |   6.11673   |   6.30136   |   6.35722   |   6.46952   |   6.7869    |
|       CURRENT (A) rms        |   46    |  3.29843   | 0.0421683 |   3.20063   |   3.27229   |   3.30422   |   3.3288    |   3.38789   |
|   CURRENT (A) peak_to_peak   |   46    |   6.5467   | 0.224928  |   5.96201   |   6.43015   |   6.5449    |   6.69109   |   7.06431   |
|       CURRENT (A) skew       |   46    | 0.00977285 | 0.0219754 | -0.0413872  | -0.00245382 |  0.0095565  |  0.0273557  |  0.0488077  |
|     CURRENT (A) kurtosis     |   46    | -0.319701  | 0.0243535 |  -0.369987  |  -0.337457  |  -0.317839  |  -0.303866  |  -0.265615  |
|   CURRENT (A) crest_factor   |   46    |  2.02663   | 0.0484798 |   1.93527   |   1.99336   |   2.02243   |   2.04711   |   2.15757   |
| CURRENT (A) Frequency Center |   46    |  3731.99   |  57.4263  |   3654.94   |   3682.58   |   3720.86   |   3769.33   |   3862.77   |
|  CURRENT (A) Spectrum Area   |   46    | 1.4158e+06 |   36923   | 1.32699e+06 | 1.39768e+06 | 1.41563e+06 | 1.43808e+06 | 1.47921e+06 |
|   CURRENT (A) Amp @ 1x RPM   |   46    |  1156.49   |  601.997  |   236.093   |   737.694   |   1029.67   |   1642.86   |   2561.94   |
|   CURRENT (A) Amp @ 2x RPM   |   46    |  1140.42   |  687.361  |   89.8997   |   632.021   |   1103.43   |   1347.17   |   3276.88   |
|   CURRENT (A) Amp @ 3x RPM   |   46    |  990.684   |  552.052  |   52.5047   |   575.717   |   933.205   |   1314.29   |   2355.52   |

Statistics from motor with mechanical damages:

|                              |  count  |    mean     |    std    |     min     |     25%     |     50%     |     75%     |     max     |
|:----------------------------:|:-------:|:-----------:|:---------:|:-----------:|:-----------:|:-----------:|:-----------:|:-----------:|
|       CURRENT (A) mean       |   46    |   3.16074   | 0.0401376 |   3.08669   |   3.13187   |   3.15845   |   3.17861   |   3.24768   |
|       CURRENT (A) std        |   46    |  0.982136   | 0.0103677 |  0.953919   |  0.975457   |  0.982334   |  0.989396   |   1.00272   |
|       CURRENT (A) max        |   46    |   6.39867   |  0.16199  |   6.12894   |   6.28244   |   6.38529   |   6.48173   |   6.83574   |
|       CURRENT (A) rms        |   46    |   3.30984   | 0.038955  |   3.24139   |   3.28201   |   3.30744   |   3.32691   |   3.39619   |
|   CURRENT (A) peak_to_peak   |   46    |   6.4676    | 0.215684  |   6.11215   |   6.34317   |   6.45396   |   6.58793   |   7.18394   |
|       CURRENT (A) skew       |   46    |  0.0305766  | 0.0185262 | -0.0107885  |  0.0156133  |  0.0297745  |  0.047472   |  0.0718401  |
|     CURRENT (A) kurtosis     |   46    |  -0.332621  | 0.0232944 |  -0.364116  |  -0.349564  |  -0.338871  |  -0.318552  |  -0.277808  |
|   CURRENT (A) crest_factor   |   46    |   2.02453   | 0.0488592 |   1.93062   |   1.98739   |   2.01599   |   2.05007   |   2.14628   |
| CURRENT (A) Frequency Center |   46    |   3659.54   |  49.9785  |   3556.9    |   3626.73   |   3673.13   |   3698.19   |   3757.83   |
|  CURRENT (A) Spectrum Area   |   46    | 1.40451e+06 |  31583.4  | 1.30868e+06 | 1.39034e+06 | 1.41112e+06 | 1.42686e+06 | 1.45709e+06 |
|   CURRENT (A) Amp @ 1x RPM   |   46    |   1264.2    |  725.121  |   108.919   |   837.711   |   1203.33   |   1718.5    |   3837.05   |
|   CURRENT (A) Amp @ 2x RPM   |   46    |   1101.25   |  634.905  |   113.061   |   580.126   |   975.247   |   1496.9    |   2411.3    |
|   CURRENT (A) Amp @ 3x RPM   |   46    |   1046.19   |  597.306  |   48.0826   |   626.218   |   926.443   |   1380.43   |   2757.53   |

Statistics from motor with electrial damage:

|                              |  count  |    mean     |    std     |     min     |     25%     |    50%     |     75%     |     max     |
|:----------------------------:|:-------:|:-----------:|:----------:|:-----------:|:-----------:|:----------:|:-----------:|:-----------:|
|       CURRENT (A) mean       |   46    |   4.11122   |  0.146102  |   3.91644   |   4.00533   |  4.09087   |   4.21077   |   4.56197   |
|       CURRENT (A) std        |   46    |  0.958563   | 0.00621466 |  0.942424   |  0.955322   |  0.958332  |  0.961858   |  0.971247   |
|       CURRENT (A) max        |   46    |   7.15177   |  0.169284  |   6.8809    |   7.03563   |  7.12016   |   7.26329   |   7.64142   |
|       CURRENT (A) rms        |   46    |   4.22161   |  0.142711  |   4.03144   |   4.11975   |  4.20099   |   4.31797   |   4.66104   |
|   CURRENT (A) peak_to_peak   |   46    |   6.06078   |  0.145585  |   5.78622   |   5.97604   |  6.04624   |   6.15213   |   6.3685    |
|       CURRENT (A) skew       |   46    |  0.0454783  | 0.0197393  |  0.0075508  |  0.0345957  | 0.0454822  |  0.056593   |  0.0924328  |
|     CURRENT (A) kurtosis     |   46    |  -0.38045   | 0.0140872  |  -0.403297  |  -0.390214  | -0.381503  |  -0.373466  |  -0.331805  |
|   CURRENT (A) crest_factor   |   46    |   1.74048   | 0.0339504  |   1.66726   |   1.71532   |  1.74138   |   1.7598    |   1.82423   |
| CURRENT (A) Frequency Center |   46    |   2789.66   |  44.0855   |   2698.04   |   2755.59   |  2797.62   |   2812.71   |   2864.8    |
|  CURRENT (A) Spectrum Area   |   46    | 1.27738e+06 |  41256.8   | 1.15628e+06 | 1.26083e+06 | 1.2864e+06 | 1.30586e+06 | 1.34823e+06 |
|   CURRENT (A) Amp @ 1x RPM   |   46    |   490.35    |  288.136   |   57.4394   |   262.31    |  520.156   |   657.273   |   1180.09   |
|   CURRENT (A) Amp @ 2x RPM   |   46    |   384.651   |  221.242   |   68.2213   |   222.588   |  326.692   |   492.078   |   1078.63   |
|   CURRENT (A) Amp @ 3x RPM   |   46    |   346.973   |  216.844   |   39.1839   |   194.196   |  315.379   |   455.713   |   979.121   |

Statistics from motor with mechanical and electrical damage:

|                              |  count  |    mean     |    std    |     min     |     25%     |     50%     |     75%     |     max     |
|:----------------------------:|:-------:|:-----------:|:---------:|:-----------:|:-----------:|:-----------:|:-----------:|:-----------:|
|       CURRENT (A) mean       |   46    |   4.36364   | 0.185386  |   4.10952   |   4.2261    |   4.32607   |   4.44731   |   4.90017   |
|       CURRENT (A) std        |   46    |  0.966841   | 0.0467897 |  0.888497   |  0.906657   |  0.988979   |   1.00517   |   1.02608   |
|       CURRENT (A) max        |   46    |   7.52579   | 0.256837  |   7.07744   |   7.32311   |   7.51141   |   7.65209   |   8.16266   |
|       CURRENT (A) rms        |   46    |   4.46958   | 0.188345  |   4.20509   |   4.32169   |   4.43375   |   4.55915   |   5.00265   |
|   CURRENT (A) peak_to_peak   |   46    |   6.17093   | 0.231159  |   5.7081    |   6.01999   |   6.15122   |   6.3093    |   6.77867   |
|       CURRENT (A) skew       |   46    |  0.0483474  | 0.0334537 | -0.0165492  |  0.017359   |  0.0521125  |  0.0708762  |  0.103741   |
|     CURRENT (A) kurtosis     |   46    |  -0.391136  | 0.0180497 |  -0.420982  |  -0.403694  |  -0.392692  |  -0.378305  |  -0.34779   |
|   CURRENT (A) crest_factor   |   46    |   1.72551   | 0.0342059 |   1.64775   |   1.69532   |   1.72575   |   1.75176   |   1.79834   |
| CURRENT (A) Frequency Center |   46    |   2822.32   |  67.0466  |   2711.51   |   2771.77   |   2813.99   |   2850.01   |   3005.22   |
|  CURRENT (A) Spectrum Area   |   46    | 1.24341e+06 |  123198   | 1.01286e+06 | 1.09404e+06 | 1.30202e+06 | 1.33011e+06 | 1.39253e+06 |
|   CURRENT (A) Amp @ 1x RPM   |   46    |   446.361   |  224.833  |   69.8026   |   245.946   |   474.077   |   589.714   |   884.945   |
|   CURRENT (A) Amp @ 2x RPM   |   46    |   326.743   |  191.88   |   24.9679   |   199.01    |   295.476   |   423.578   |   812.538   |
|   CURRENT (A) Amp @ 3x RPM   |   46    |   366.484   |  197.136  |   17.6981   |   234.405   |   329.594   |   512.49    |   900.408   |

The following sections detail each current-derived variable used in the analysis.


#### `CURRENT (A) mean`

* **Definition:** The average current amplitude recorded over a 0.8-second steady-state sample.
* **Distribution Plot:**

    ![Overall Distribution of CURRENT (A) mean compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_CURRENT_(A)_mean.png)

* **Histogram:**

    ![Overall Histogram of CURRENT (A) mean compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_CURRENT_(A)_mean.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of CURRENT (A) st by Motor Type](../../Output/DataAppendixOutput/boxplot_CURRENT_(A)_mean_by_Class.png)

#### `CURRENT (A) std`

* **Definition:** The standard deviation of the current amplitude, indicating the spread or variability of current readings over a 0.8-second steady-state sample.
* **Distribution Plot:**

    ![Overall Distribution of CURRENT (A) std compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_CURRENT_(A)_std.png)

* **Histogram:**

    ![Overall Histogram of CURRENT (A) std compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_CURRENT_(A)_std.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of CURRENT (A) std by Motor Type](../../Output/DataAppendixOutput/boxplot_CURRENT_(A)_std_by_Class.png)

#### `CURRENT (A) max`

* **Definition:** The maximum current amplitude recorded over a 0.8-second steady-state.
* **Distribution Plot:**

    ![Overall Distribution of CURRENT (A) max compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_CURRENT_(A)_max.png)

* **Histogram:**

    ![Overall Histogram of CURRENT (A) max compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_CURRENT_(A)_max.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of CURRENT (A) max by Motor Type](../../Output/DataAppendixOutput/boxplot_CURRENT_(A)_max_by_Class.png)

#### `CURRENT (A) rms`

* **Definition:** The Root Mean Square (RMS) value of the current over a 0.8-second steady-state sample.
* **Distribution Plot:**

    ![Overall Distribution of CURRENT (A) rms compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_CURRENT_(A)_rms.png)

* **Histogram:**

    ![Overall Histogram of CURRENT (A) rms compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_CURRENT_(A)_rms.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of CURRENT (A) rms by Motor Type](../../Output/DataAppendixOutput/boxplot_CURRENT_(A)_rms_by_Class.png)


#### `CURRENT (A) peak_to_peak`

* **Definition:** The difference between the maximum and minimum current amplitudes recorded over a 0.8-second steady-state sample.
* **Distribution Plot:**

    ![Overall Distribution of CURRENT (A) peak_to_peak compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_CURRENT_(A)_peak_to_peak.png)

* **Histogram:**

    ![Overall Histogram of CURRENT (A) peak_to_peak compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_CURRENT_(A)_peak_to_peak.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of CURRENT (A) peak_to_peak by Motor Type](../../Output/DataAppendixOutput/boxplot_CURRENT_(A)_peak_to_peak_by_Class.png)

#### `CURRENT (A) skew`

* **Definition:** A measure of the asymmetry of the current distribution. A positive skew indicates a longer tail to the right, and a negative skew indicates a longer tail to the left.
* **Distribution Plot:**

    ![Overall Distribution of CURRENT (A) skew compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_CURRENT_(A)_skew.png)

* **Histogram:**

    ![Overall Histogram of CURRENT (A) skew compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_CURRENT_(A)_skew.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of CURRENT (A) skew by Motor Type](../../Output/DataAppendixOutput/boxplot_CURRENT_(A)_skew_by_Class.png)


#### `CURRENT (A) kurtosis`

* **Definition:**  A measure of the "tailedness" of the current distribution. High kurtosis indicates more extreme outliers, while low kurtosis indicates fewer and less extreme outliers.
* **Distribution Plot:**

    ![Overall Distribution of CURRENT (A) kurtosis compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_CURRENT_(A)_kurtosis.png)

* **Histogram:**

    ![Overall Histogram of CURRENT (A) kurtosis compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_CURRENT_(A)_kurtosis.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of CURRENT (A) kurtosis by Motor Type](../../Output/DataAppendixOutput/boxplot_CURRENT_(A)_kurtosis_by_Class.png)

#### `CURRENT (A) crest_factor`

* **Definition:**  The ratio of the peak (maximum) current to the RMS current, indicating the presence of peaks in the waveform.
* **Distribution Plot:**

    ![Overall Distribution of CURRENT (A) crest_factor compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_CURRENT_(A)_crest_factor.png)

* **Histogram:**

    ![Overall Histogram of CURRENT (A) crest_factor compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_CURRENT_(A)_crest_factor.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of CURRENT (A) crest_factor by Motor Type](../../Output/DataAppendixOutput/boxplot_CURRENT_(A)_crest_factor_by_Class.png)

#### `CURRENT (A) Frequency Center`

* **Definition:**  The weighted average frequency of the current spectrum, indicating the central tendency of the frequency content.
* **Distribution Plot:**

    ![Overall Distribution of CURRENT (A) Frequency Center compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_CURRENT_(A)_crest_factor.png)

* **Histogram:**

    ![Overall Histogram of CURRENT (A) Frequency Center compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_CURRENT_(A)_crest_factor.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of CURRENT (A) Frequency Center by Motor Type](../../Output/DataAppendixOutput/boxplot_CURRENT_(A)_crest_factor_by_Class.png)

#### `CURRENT (A) Spectrum Area`

* **Definition:**  The total area under the current frequency spectrum, which can be related to the total power or energy of the signal.
* **Distribution Plot:**

    ![Overall Distribution of CURRENT (A) Spectrum Area compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_CURRENT_(A)_Spectrum_Area.png)

* **Histogram:**

    ![Overall Histogram of CURRENT (A) Spectrum Area compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_CURRENT_(A)_Spectrum_Area.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of CURRENT (A) Spectrum Area by Motor Type](../../Output/DataAppendixOutput/boxplot_CURRENT_(A)_Spectrum_Area_by_Class.png)

#### `CURRENT (A) Amp @ 1x RPM`

* **Definition:**  The amplitude of the current signal at the fundamental rotational frequency (1 times RPM), often indicative of specific mechanical imbalances.
* **Distribution Plot:**

    ![Overall Distribution of CURRENT (A) Amp @ 1x RPM compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_CURRENT_(A)_Amp_@_1x_RPM.png)

* **Histogram:**

    ![Overall Histogram of CURRENT (A) Amp @ 1x RPM compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_CURRENT_(A)_Amp_@_1x_RPM.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of CURRENT (A) Amp @ 1x RPM by Motor Type](../../Output/DataAppendixOutput/boxplot_CURRENT_(A)_Amp_@_1x_RPM_by_Class.png)

#### `CURRENT (A) Amp @ 2x RPM`

* **Definition:**  The amplitude of the current signal at the fundamental rotational frequency (2 times RPM), often indicative of specific mechanical imbalances.
* **Distribution Plot:**

    ![Overall Distribution of CURRENT (A) Amp @ 2x RPM compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_CURRENT_(A)_Amp_@_2x_RPM.png)

* **Histogram:**

    ![Overall Histogram of CURRENT (A) Amp @ 2x RPM compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_CURRENT_(A)_Amp_@_2x_RPM.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of CURRENT (A) Amp @ 2x RPM by Motor Type](../../Output/DataAppendixOutput/boxplot_CURRENT_(A)_Amp_@_2x_RPM_by_Class.png)

#### `CURRENT (A) Amp @ 3x RPM`

* **Definition:**  The amplitude of the current signal at the fundamental rotational frequency (3 times RPM), often indicative of specific mechanical imbalances.
* **Distribution Plot:**

    ![Overall Distribution of CURRENT (A) Amp @ 3x RPM compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_CURRENT_(A)_Amp_@_3x_RPM.png)

* **Histogram:**

    ![Overall Histogram of CURRENT (A) Amp @ 3x RPM compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_CURRENT_(A)_Amp_@_3x_RPM.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of ROTO (RPM) Amp @ 1x RPM by Motor Type](../../Output/DataAppendixOutput/boxplot_CURRENT_(A)_Amp_@_3x_RPM_by_Class.png)



## II. ROTATIONAL SPEED (ROTO RPM) Domain

Rotational speed (RPM - Revolutions Per Minute) and its characteristics are critical indicators of the motor's mechanical operation and can reveal various fault conditions. The following sections detail each RPM-derived variable.

![Rotational speed over time in example experiment per motor](../../Output/DataAppendixOutput/plot_roto_whole_experiment.png)
![Rotational speed  over time in example sample per motor](../../Output/DataAppendixOutput/plot_roto_sample.png)

Overall statistics from ROTO RPM domain for whole population:

|                             |  count  |    mean     |     std     |     min     |     25%     |     50%     |     75%     |    max     |
|:---------------------------:|:-------:|:-----------:|:-----------:|:-----------:|:-----------:|:-----------:|:-----------:|:----------:|
|       ROTO (RPM) mean       |   184   |   22299.5   |   574.565   |   21623.9   |   21736.9   |   22242.6   |    22864    |  22996.8   |
|       ROTO (RPM) std        |   184   |   519.286   |   6.40075   |   496.796   |   514.505   |   519.117   |   523.82    |  535.455   |
|       ROTO (RPM) max        |   184   |   24485.1   |   601.055   |   23542.4   |   23917.4   |   24514.4   |   25049.6   |   25433    |
|       ROTO (RPM) rms        |   184   |   22305.5   |   574.51    |   21629.9   |   21743.1   |   22248.6   |    22870    |  23002.9   |
|   ROTO (RPM) peak_to_peak   |   184   |   4633.94   |   168.838   |   4185.55   |   4517.05   |   4640.27   |   4751.66   |  5186.54   |
|       ROTO (RPM) skew       |   184   |  -0.113846  | 0.00892184  |  -0.140152  |  -0.120144  |  -0.113562  |  -0.107704  | -0.090716  |
|     ROTO (RPM) kurtosis     |   184   |   0.56374   |  0.0847713  |  0.308897   |  0.502061   |  0.568182   |  0.633998   |  0.789741  |
|   ROTO (RPM) crest_factor   |   184   |   1.09806   | 0.00640614  |   1.08489   |   1.0925    |   1.0988    |   1.10292   |  1.11914   |
| ROTO (RPM) Frequency Center |   184   |   9575.09   |   168.954   |   9123.76   |   9457.81   |   9575.76   |   9731.83   |   9839.7   |
|  ROTO (RPM) Spectrum Area   |   184   | 1.88039e+09 | 2.46922e+07 | 1.81435e+09 | 1.86474e+09 | 1.87886e+09 | 1.90034e+09 | 1.9315e+09 |
|   ROTO (RPM) Amp @ 1x RPM   |   184   |   128078    |   82854.4   |   9137.75   |   71635.8   |   113363    |   175915    |   753454   |
|   ROTO (RPM) Amp @ 2x RPM   |   184   |   101767    |   57486.3   |   6802.71   |   64477.4   |   94006.6   |   124700    |   334238   |
|   ROTO (RPM) Amp @ 3x RPM   |   184   |   101767    |   57486.3   |   6802.71   |   64477.4   |   94006.6   |   124700    |   334238   |

Statistics from motor without damages:

|                             |  count  |    mean     |     std     |     min     |     25%     |     50%     |     75%     |     max     |
|:---------------------------:|:-------:|:-----------:|:-----------:|:-----------:|:-----------:|:-----------:|:-----------:|:-----------:|
|       ROTO (RPM) mean       |   46    |   21684.1   |   38.2416   |   21623.9   |   21657.5   |   21683.1   |   21711.6   |   21755.9   |
|       ROTO (RPM) std        |   46    |   512.427   |   4.55179   |   496.796   |   510.423   |   512.47    |   515.433   |   519.404   |
|       ROTO (RPM) max        |   46    |   23842.3   |   151.297   |   23542.4   |   23737.7   |   23853.7   |   23933.4   |   24209.2   |
|       ROTO (RPM) rms        |   46    |   21690.2   |   38.2881   |   21629.9   |   21663.5   |   21689.1   |   21717.6   |   21762.1   |
|   ROTO (RPM) peak_to_peak   |   46    |   4547.69   |   168.121   |   4185.55   |   4417.1    |   4596.77   |   4657.06   |   4982.07   |
|       ROTO (RPM) skew       |   46    |   -0.1072   | 0.00829982  |  -0.130304  |  -0.111483  |  -0.106489  |  -0.10215   |  -0.090716  |
|     ROTO (RPM) kurtosis     |   46    |  0.524363   |  0.0676406  |  0.386238   |   0.48765   |   0.52576   |  0.568617   |  0.688935   |
|   ROTO (RPM) crest_factor   |   46    |   1.09953   | 0.00669995  |   1.08696   |   1.0948    |   1.10015   |   1.10346   |   1.11914   |
| ROTO (RPM) Frequency Center |   46    |   9684.8    |   73.8329   |   9529.43   |   9643.11   |   9679.86   |   9746.25   |   9810.69   |
|  ROTO (RPM) Spectrum Area   |   46    | 1.85478e+09 | 1.66282e+07 | 1.81435e+09 | 1.84745e+09 | 1.85334e+09 | 1.86716e+09 | 1.88394e+09 |
|   ROTO (RPM) Amp @ 1x RPM   |   46    |   139161    |   116516    |   9137.75   |   75387.8   |   108645    |   191703    |   753454    |
|   ROTO (RPM) Amp @ 2x RPM   |   46    |   107060    |   55560.2   |   19338.4   |   70497.8   |   100355    |   119602    |   334238    |
|   ROTO (RPM) Amp @ 3x RPM   |   46    |   107060    |   55560.2   |   19338.4   |   70497.8   |   100355    |   119602    |   334238    |

Statistics from motor with mechanical damages:

|                             |  count  |    mean     |     std     |     min     |     25%     |     50%     |     75%     |     max     |
|:---------------------------:|:-------:|:-----------:|:-----------:|:-----------:|:-----------:|:-----------:|:-----------:|:-----------:|
|       ROTO (RPM) mean       |   46    |   21783.6   |   40.7009   |   21689.3   |   21752.7   |    21778    |   21817.3   |   21857.6   |
|       ROTO (RPM) std        |   46    |   518.267   |   3.56922   |   510.149   |   516.449   |   518.551   |   520.076   |   527.785   |
|       ROTO (RPM) max        |   46    |   23975.8   |   138.541   |   23673.6   |   23906.3   |   23962.8   |   24075.3   |   24338.9   |
|       ROTO (RPM) rms        |   46    |   21789.7   |   40.725    |   21695.3   |   21758.8   |   21784.2   |   21823.4   |   21863.8   |
|   ROTO (RPM) peak_to_peak   |   46    |   4594.79   |   131.143   |   4290.84   |   4523.15   |   4615.09   |   4699.78   |   4863.05   |
|       ROTO (RPM) skew       |   46    |  -0.114235  | 0.00718984  |  -0.128932  |  -0.119089  |  -0.114516  |  -0.109304  | -0.0977547  |
|     ROTO (RPM) kurtosis     |   46    |  0.486694   |  0.0597308  |  0.308897   |  0.451374   |  0.477018   |  0.517791   |  0.641794   |
|   ROTO (RPM) crest_factor   |   46    |   1.10064   | 0.00599847  |   1.08863   |   1.09734   |   1.1005    |   1.10456   |   1.11381   |
| ROTO (RPM) Frequency Center |   46    |   9748.76   |   55.6092   |   9541.91   |   9726.16   |   9760.85   |   9782.81   |   9839.7    |
|  ROTO (RPM) Spectrum Area   |   46    | 1.87481e+09 | 1.26114e+07 | 1.82463e+09 | 1.86977e+09 | 1.87693e+09 | 1.88095e+09 | 1.89334e+09 |
|   ROTO (RPM) Amp @ 1x RPM   |   46    |   134863    |   73370.9   |   19163.1   |   81389.1   |   129182    |   180045    |   346503    |
|   ROTO (RPM) Amp @ 2x RPM   |   46    |   102587    |   65165.2   |   9793.43   |   60227.1   |   91954.2   |   125424    |   318935    |
|   ROTO (RPM) Amp @ 3x RPM   |   46    |   102587    |   65165.2   |   9793.43   |   60227.1   |   91954.2   |   125424    |   318935    |

Statistics from motor with electrial damage:

|                             |  count  |    mean     |    std     |     min     |    25%    |     50%     |     75%     |    max     |
|:---------------------------:|:-------:|:-----------:|:----------:|:-----------:|:---------:|:-----------:|:-----------:|:----------:|
|       ROTO (RPM) mean       |   46    |    22965    |  22.2577   |   22900.8   |  22948.2  |   22971.2   |   22982.8   |  22996.8   |
|       ROTO (RPM) std        |   46    |    525.8    |  4.15972   |   516.766   |  522.933  |   525.904   |   528.738   |  535.455   |
|       ROTO (RPM) max        |   46    |   25149.8   |   151.27   |   24895.9   |  25022.9  |   25140.8   |   25292.6   |   25433    |
|       ROTO (RPM) rms        |   46    |   22971.1   |  22.2869   |   22906.8   |  22954.2  |   22977.1   |   22988.9   |  23002.9   |
|   ROTO (RPM) peak_to_peak   |   46    |   4691.25   |  175.063   |   4411.39   |  4518.57  |   4750.9    |   4811.93   |  5186.54   |
|       ROTO (RPM) skew       |   46    |  -0.11988   | 0.00822331 |  -0.140152  | -0.124194 |  -0.120381  |  -0.113642  | -0.0998876 |
|     ROTO (RPM) kurtosis     |   46    |  0.609736   | 0.0591902  |  0.490828   | 0.571862  |  0.615493   |  0.647616   |  0.745877  |
|   ROTO (RPM) crest_factor   |   46    |   1.09513   | 0.00650365 |   1.08489   |  1.08946  |   1.09567   |   1.10116   |  1.10657   |
| ROTO (RPM) Frequency Center |   46    |   9418.33   |  91.2098   |   9123.76   |  9379.23  |   9435.78   |   9478.15   |  9563.13   |
|  ROTO (RPM) Spectrum Area   |   46    | 1.89954e+09 | 1.7064e+07 | 1.84916e+09 | 1.891e+09 | 1.90176e+09 | 1.91082e+09 | 1.9315e+09 |
|   ROTO (RPM) Amp @ 1x RPM   |   46    |   111377    |  61587.3   |   13146.7   |  65646.3  |   99330.7   |   156481    |   314182   |
|   ROTO (RPM) Amp @ 2x RPM   |   46    |   115434    |  61818.8   |   6802.71   |  79315.1  |   113362    |   148016    |   333877   |
|   ROTO (RPM) Amp @ 3x RPM   |   46    |   115434    |  61818.8   |   6802.71   |  79315.1  |   113362    |   148016    |   333877   |

Statistics from motor with mechanical and electrical damage:

|                             |  count  |    mean     |     std     |    min     |     25%     |     50%     |     75%     |     max     |
|:---------------------------:|:-------:|:-----------:|:-----------:|:----------:|:-----------:|:-----------:|:-----------:|:-----------:|
|       ROTO (RPM) mean       |   46    |   22765.2   |   71.8299   |  22627.5   |   22705.1   |   22775.8   |   22832.4   |   22851.8   |
|       ROTO (RPM) std        |   46    |   520.648   |   4.62881   |  509.538   |   518.374   |   521.477   |   524.133   |   527.605   |
|       ROTO (RPM) max        |   46    |   24972.6   |   148.439   |  24689.9   |   24836.3   |   24948.5   |   25103.4   |   25214.8   |
|       ROTO (RPM) rms        |   46    |   22771.2   |   71.8106   |  22633.3   |   22711.2   |   22781.7   |   22838.3   |   22857.7   |
|   ROTO (RPM) peak_to_peak   |   46    |   4702.03   |   150.152   |  4409.86   |   4597.16   |   4692.15   |   4799.34   |   5073.63   |
|       ROTO (RPM) skew       |   46    |  -0.11407   | 0.00727501  | -0.129279  |  -0.119265  |  -0.113469  |  -0.109128  |  -0.101799  |
|     ROTO (RPM) kurtosis     |   46    |  0.634167   |  0.0518796  |  0.52234   |  0.599194   |  0.636199   |  0.663846   |  0.789741   |
|   ROTO (RPM) crest_factor   |   46    |   1.09696   | 0.00497415  |  1.08768   |   1.09276   |   1.09652   |   1.10005   |   1.10732   |
| ROTO (RPM) Frequency Center |   46    |   9448.48   |   120.76    |  9179.33   |   9329.74   |   9482.57   |   9538.32   |   9649.13   |
|  ROTO (RPM) Spectrum Area   |   46    | 1.89243e+09 | 2.29608e+07 | 1.8418e+09 | 1.87009e+09 | 1.89693e+09 | 1.90969e+09 | 1.93025e+09 |
|   ROTO (RPM) Amp @ 1x RPM   |   46    |   126913    |   68597.1   |  12163.1   |   69946.5   |   121430    |   172336    |   294532    |
|   ROTO (RPM) Amp @ 2x RPM   |   46    |   81988.3   |    40790    |  7927.41   |   52514.9   |   85676.8   |   100298    |   184891    |
|   ROTO (RPM) Amp @ 3x RPM   |   46    |   81988.3   |    40790    |  7927.41   |   52514.9   |   85676.8   |   100298    |   184891    |

The following sections detail each current-derived variable used in the analysis.



#### `ROTO (RPM) mean`

* **Definition:** The average rotational speed amplitude recorded over a 0.8-second steady-state sample.
* **Distribution Plot:**

    ![Overall Distribution of ROTO (RPM) mean compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_ROTO_(RPM)_mean.png)

* **Histogram:**

    ![Overall Histogram of ROTO (RPM) mean compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_ROTO_(RPM)_mean.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of ROTO (RPM) mean by Motor Type](../../Output/DataAppendixOutput/boxplot_ROTO_(RPM)_mean_by_Class.png)

#### `ROTO (RPM) std`

* **Definition:** The standard deviation of the rotational speed amplitude, indicating the spread or variability of rotational speed readings over a 0.8-second steady-state sample.
* **Distribution Plot:**

    ![Overall Distribution of ROTO (RPM) std compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_ROTO_(RPM)_std.png)

* **Histogram:**

    ![Overall Histogram of ROTO (RPM) std compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_ROTO_(RPM)_std.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of ROTO (RPM) std by Motor Type](../../Output/DataAppendixOutput/boxplot_ROTO_(RPM)_std_by_Class.png)

#### `ROTO (RPM) max`

* **Definition:** The maximum rotational speed amplitude recorded over a 0.8-second steady-state.
* **Distribution Plot:**

    ![Overall Distribution of ROTO (RPM) max compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_ROTO_(RPM)_max.png)

* **Histogram:**

    ![Overall Histogram of ROTO (RPM) max compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_ROTO_(RPM)_max.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of ROTO (RPM) max by Motor Type](../../Output/DataAppendixOutput/boxplot_ROTO_(RPM)_max_by_Class.png)

#### `ROTO (RPM) rms`

* **Definition:** The Root Mean Square (RMS) value of the rotational speed over a 0.8-second steady-state sample.
* **Distribution Plot:**

    ![Overall Distribution of ROTO (RPM) rms compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_ROTO_(RPM)_rms.png)

* **Histogram:**

    ![Overall Histogram of ROTO (RPM) rms compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_ROTO_(RPM)_rms.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of ROTO (RPM) rms by Motor Type](../../Output/DataAppendixOutput/boxplot_ROTO_(RPM)_rms_by_Class.png)


#### `ROTO (RPM) peak_to_peak`

* **Definition:** The difference between the maximum and minimum rotational speed amplitudes recorded over a 0.8-second steady-state sample.
* **Distribution Plot:**

    ![Overall Distribution of ROTO (RPM) peak_to_peak compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_ROTO_(RPM)_peak_to_peak.png)

* **Histogram:**

    ![Overall Histogram of ROTO (RPM) peak_to_peak compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_ROTO_(RPM)_peak_to_peak.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of ROTO (RPM) peak_to_peak by Motor Type](../../Output/DataAppendixOutput/boxplot_ROTO_(RPM)_peak_to_peak_by_Class.png)

#### `ROTO (RPM) skew`

* **Definition:** A measure of the asymmetry of the rotational speed distribution. A positive skew indicates a longer tail to the right, and a negative skew indicates a longer tail to the left.
* **Distribution Plot:**

    ![Overall Distribution of ROTO (RPM) skew compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_ROTO_(RPM)_skew.png)

* **Histogram:**

    ![Overall Histogram of ROTO (RPM) skew compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_ROTO_(RPM)_skew.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of ROTO (RPM) skew by Motor Type](../../Output/DataAppendixOutput/boxplot_ROTO_(RPM)_skew_by_Class.png)


#### `ROTO (RPM) kurtosis`

* **Definition:**  A measure of the "tailedness" of the rotational speed distribution. High kurtosis indicates more extreme outliers, while low kurtosis indicates fewer and less extreme outliers.
* **Distribution Plot:**

    ![Overall Distribution of ROTO (RPM) kurtosis compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_ROTO_(RPM)_kurtosis.png)

* **Histogram:**

    ![Overall Histogram of ROTO (RPM) kurtosis compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_ROTO_(RPM)_kurtosis.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of ROTO (RPM) kurtosis by Motor Type](../../Output/DataAppendixOutput/boxplot_ROTO_(RPM)_kurtosis_by_Class.png)

#### `ROTO (RPM) crest_factor`

* **Definition:**  The ratio of the peak (maximum) rotational speed to the RMS rotational speed, indicating the presence of peaks in the waveform.
* **Distribution Plot:**

    ![Overall Distribution of ROTO (RPM) crest_factor compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_ROTO_(RPM)_crest_factor.png)

* **Histogram:**

    ![Overall Histogram of ROTO (RPM) crest_factor compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_ROTO_(RPM)_crest_factor.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of ROTO (RPM) crest_factor by Motor Type](../../Output/DataAppendixOutput/boxplot_ROTO_(RPM)_crest_factor_by_Class.png)

#### `ROTO (RPM) Frequency Center`

* **Definition:**  The weighted average frequency of the rotational speed spectrum, indicating the central tendency of the frequency content.
* **Distribution Plot:**

    ![Overall Distribution of ROTO (RPM) Frequency Center compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_ROTO_(RPM)_crest_factor.png)

* **Histogram:**

    ![Overall Histogram of ROTO (RPM) Frequency Center compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_ROTO_(RPM)_crest_factor.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of ROTO (RPM) Frequency Center by Motor Type](../../Output/DataAppendixOutput/boxplot_ROTO_(RPM)_crest_factor_by_Class.png)

#### `ROTO (RPM) Spectrum Area`

* **Definition:**  The total area under the rotational speed frequency spectrum, which can be related to the total power or energy of the signal.
* **Distribution Plot:**

    ![Overall Distribution of ROTO (RPM) Spectrum Area compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_ROTO_(RPM)_Spectrum_Area.png)

* **Histogram:**

    ![Overall Histogram of ROTO (RPM) Spectrum Area compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_ROTO_(RPM)_Spectrum_Area.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of ROTO (RPM) Spectrum Area by Motor Type](../../Output/DataAppendixOutput/boxplot_ROTO_(RPM)_Spectrum_Area_by_Class.png)

#### `ROTO (RPM) Amp @ 1x RPM`

* **Definition:**  The amplitude of the rotational speed signal at the fundamental rotational frequency (1 times RPM), often indicative of specific mechanical imbalances.
* **Distribution Plot:**

    ![Overall Distribution of ROTO (RPM) Amp @ 1x RPM compared to all Motor Types](../../Output/DataAppendixOutput/density_layout_ROTO_(RPM)_Amp_@_1x_RPM.png)

* **Histogram:**

    ![Overall Histogram of ROTO (RPM) Amp @ 1x RPM compared to all Motor Types](../../Output/DataAppendixOutput/histogram_layout_ROTO_(RPM)_Amp_@_1x_RPM.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of ROTO (RPM) Amp @ 1x RPM by Motor Type](./DataAppendixOutput/boxplot_ROTO_(RPM)_Amp_@_1x_RPM_by_Class.png)

#### `ROTO (RPM) Amp @ 2x RPM`

* **Definition:**  The amplitude of the rotational speed signal at the fundamental rotational frequency (2 times RPM), often indicative of specific mechanical imbalances.
* **Distribution Plot:**

    ![Overall Distribution of ROTO (RPM) Amp @ 2x RPM compared to all Motor Types](./DataAppendixOutput/density_layout_ROTO_(RPM)_Amp_@_2x_RPM.png)

* **Histogram:**

    ![Overall Histogram of ROTO (RPM) Amp @ 2x RPM compared to all Motor Types](./DataAppendixOutput/histogram_layout_ROTO_(RPM)_Amp_@_2x_RPM.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of ROTO (RPM) Amp @ 2x RPM by Motor Type](./DataAppendixOutput/boxplot_ROTO_(RPM)_Amp_@_2x_RPM_by_Class.png)

#### `ROTO (RPM) Amp @ 3x RPM`

* **Definition:**  The amplitude of the rotational speed signal at the fundamental rotational frequency (3 times RPM), often indicative of specific mechanical imbalances.
* **Distribution Plot:**

    ![Overall Distribution of ROTO (RPM) Amp @ 3x RPM compared to all Motor Types](./DataAppendixOutput/density_layout_ROTO_(RPM)_Amp_@_3x_RPM.png)

* **Histogram:**

    ![Overall Histogram of ROTO (RPM) Amp @ 3x RPM compared to all Motor Types](./DataAppendixOutput/histogram_layout_ROTO_(RPM)_Amp_@_3x_RPM.png)

* **Box Plot by Motor Damage Type:**

    ![Box Plot of ROTO (RPM) Amp @ 3x RPM by Motor Type](./DataAppendixOutput/boxplot_ROTO_(RPM)_Amp_@_3x_RPM_by_Class.png)

