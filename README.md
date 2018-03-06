# Distance-Based Sampling (Supplementary Website)

Note that we have included the plots and tables as pdf.
However, the anonymization tool does not allow accessing any files but text files.
Therefore, we have uploaded the plots as pictures and embedded them in this README.

In Section 1, we show the variances of the sampling strategies.
In Section 2, we show the results of the comparison of different machine-learning techniques.
In Section 3, we show the results of applying distance-based sampling on numeric configuration options.

## 1 Variance of the Sampling Strategies

For a detailed view on the variances of the sampling strategies on the subject systems in the sample sizes *t=1*, *t=2*, and *t=3*, we provide the following table.

[![](https://preview.ibb.co/daJGnn/Variances.png)](https://image.ibb.co/nyZYYS/Variances.png)

In the figure above, we illustrate the variances of all error rates as box-plots.
It is important to note, that t-wise sampling has no variance in our setup.


## 2 Machine-Learning Techniques

In the parallel line of experiments, we compared six different machine-learning techniques:
* Classification Ad Regression Trees (CART)
* k-Nearest Neighbors (knn)
* Kernel Ridge Regression (KRR)
* Multivariable Regression (MR)
* Random Forest (RF)
* Support Vector Machines (SVR)

The comparison was performed on software systems that contain binary and numeric configuration options.
Thus, we used binary **and** numeric sampling strategies.
The binary sampling strategies are:
* Option-Wise (OW)
* Negative Option-Wise (NegOW)
* Pair-Wise / t-wise with *t=2* (T2)
* Tripple-Wise / t-wise with *t=3* (T3)

In the following table, we illustrate the results of the comparison as a heat map.

[![](https://preview.ibb.co/kG2ntS/Machine_Learning_Techniques2.jpg)](https://image.ibb.co/kG2ntS/Machine_Learning_Techniques2.jpg)

In this table, the binary sampling strategies are displayed column-wise.
On the diagonal, we show the prediction error of the respective machine-learning technique.
For the plots not on the diagonal, we show the difference between the machine-learning technique in the row to the machine-learning technique in the column.
The green color indicates that the machine-learning technique in the column is more accurate, whereas the red color indicates that the machine-learning technique in the row is more accurate.
As we can see, CART, MR, and RF outperform the other machine-learning strategies.
However, RF has slightly lower error rates than CART and MR, as can be seen on the diagonal.

## 3 Numeric Configuration Options

In the following, we present the first results for case studies with numeric configuration options, since distance-based sampling is also applicable for numeric configuration options.
Note that we have converted the numeric configuration options into binary configuration options in the paper.

![Table containing the results for numeric case studies (If this text is shown, the picture can not be displayed)](https://preview.ibb.co/hN2fxn/table.png)

In the figure above, we have only highlighted the results where distance-based sampling achieved better mean error rates than t-wise sampling.
As we see, distance-based sampling achieves better results than t-wise sampling in nearly all cases.
Only in 7z and JavaGC on sample size *t=1*, distance-based sampling performs worse.
