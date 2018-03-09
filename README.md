# Distance-Based Sampling (Supplementary Website)

In the first part, we show the variances of the sampling strategies. 
Then, in part 2, we show the results when paring different machine-learning techniques with respect to their accuracy in predicting all configurations. 
Last, we briefly describe the location of the raw data.

## 1 Variance of the Sampling Strategies

For a detailed view on the variances of the sampling strategies on the subject systems in the sample sizes *t=1*, *t=2*, and *t=3*, we provide the following table.

[![](https://preview.ibb.co/daJGnn/Variances.png)](https://image.ibb.co/nyZYYS/Variances.png)


## 2 Machine-Learning Techniques

In the parallel line of experiments, we compared six different machine-learning techniques:
* Classification Ad Regression Trees (CART)
* k-Nearest Neighbors (knn)
* Kernel Ridge Regression (KRR)
* Multiple linear Regression (MR)
* Random Forest (RF)
* Support Vector Machines (SVR)

In the paper, we have used MR.

The comparison was performed on software systems that contain binary and numeric configuration options.
Thus, we used binary **and** numeric sampling strategies.
The binary sampling strategies are:
* Option-Wise (OW)
* Negative Option-Wise (NegOW)
* Pair-Wise / t-wise with *t=2* (T2)
* Tripple-Wise / t-wise with *t=3* (T3)

In the following table, we illustrate the results of the comparison as a heat map.

[![](https://preview.ibb.co/kG2ntS/Machine_Learning_Techniques2.jpg)](https://image.ibb.co/kG2ntS/Machine_Learning_Techniques2.jpg)

In the table, we perform a pair-wise comparison of the machine-learning techniques with respect to their accuracy in predicting the performance of all configurations. On the diagonal, we show the prediction error of the respective machine-learning technique. 
For the plots not on the diagonal, we show the difference between the machine-learning technique in the row to the machine-learning technique in the column. 
The green color indicates that the machine-learning technique in the column is more accurate, whereas the red color indicates that the machine-learning technique in the row is more accurate. 
As we can see, CART, MR, and RF outperform the other machine-learning technique. 
However, RF has slightly lower error rates than CART and MR, as can be seen on the diagonal. 
Besides, we also see that the accuracy of the machine-learning technique strongly depends on the learning set. 

## 3 Raw Data

The raw data for the subject systems can be accessed in the directory *Results*, which has two subdirectories, *RawData_Summary* and *RawData*.
In the directory *RawData_Summary*, we have summarized our results in different csv-files and provide the feature models (a.k.a. variability models), whereas the results of all 100 runs of all subject systems are stored in the directory *RawData*.
