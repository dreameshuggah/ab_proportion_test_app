AB Proportion Test Streamlit App:

https://ab-proportion-test.streamlit.app/

# 📊 A/B Proportion Test Calculator

A streamlined, interactive web application built with **Streamlit** to help marketers, product managers, and data analysts determine the statistical significance of A/B test results for proportions.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ab-proportion-test.streamlit.app/)

## 🚀 Overview

This app simplifies the process of analyzing A/B tests where the primary metric is a **proportion** (e.g., conversion rate, click-through rate, or churn). By inputting the number of visitors and conversions for two groups, the app automatically calculates the statistical significance, p-value, and confidence intervals to help you make data-driven decisions.

## ✨ Features

- **Instant Statistical Analysis:** Performs a Two-Proportion Parametric (Z-test) or Non-Parametric (Fisher's Exact) methods based on sample sizes.
- **Conversion Comparison:** View the uplift (or drop) between your Control and Variant groups.
- **Significance Indicators:** Clear "Statistically Significant" vs. "Not Significant" verdicts based on a %5 Alpha ($\alpha$).
- **Confidence Intervals:** Calculates the range of likely values for the true difference between groups.
- **Visualizations:** Dynamic charts showing the probability distributions of both groups.
- **Sample Size Insights:** Understand if your current data is sufficient to draw a conclusive result.

## 🛠️ How to Use

1.  **Input Data:** In the sidebar or main panel, enter the:
    * **Sample Size ($n$):** Total number of users/visitors for Group A and Group B.
    * **Conversions ($x$):** Number of successful actions (clicks, signups, etc.) for each group.
2.  **Set Significance Level:** Choose your threshold (typically 0.05 for 95% confidence).
3.  **Select Hypothesis:** Choose between a One-sided test.
4.  **Review Results:** The app will output:
    * Conversion rates for both groups.
    * The **Z-Statistic** and **P-Value**.
    * The **Relative Lift** (e.g., "Variant performed 12% better than Control").
    
