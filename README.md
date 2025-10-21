# **KM Master Discrepancy Detection System**

![Python Code](https://img.shields.io/badge/Python-Code-blue?logo=python&logoColor=white)
![Sheets API](https://img.shields.io/badge/Google_Sheets-API-34A853?logo=googlesheets&logoColor=white)

A systematic framework designed to identify and prioritize discrepancies in KM Master data. This system provides **KM Master recommendations** for each store. It enables the operations team to efficiently determine and prioritize which KM Master data entries should be validated for each store.

## 🎯 **Problem**

The KM Master data represents the round-trip distance between an Operating Point and a Store. It serves as a crucial reference for determining transportation costs (*Uang Jalan Pengiriman* or **UJP**).

An inaccurate KM Master can lead to significant problems: **underestimated distances** may cause operational problems, while **overestimated distances** may create opportunities for frauds. Therefore, it requires regular validation to ensure accuracy.

However, manually validating all thousands of KM Master entries for each store is highly inefficient. As a result, the operations team must prioritize which KM Master data should be validated first.

## 💡 **Solution**

A rule-based framework that applies three methods to generate **KM Master recommendations**. The system prioritizes methods in the following order:

1. **KM Master Method**
2. **KM Tempuh Method**
3. **Master Zona Method**

If a recommendation is available from a higher-priority method (e.g, KM Master), the lower-priority methods (e.g, KM Tempuh) will be ignored.

For detailed explanation, go to [notebooks](https://github.com/MNAtthoriq/km-master-discrepancy-detection-system/tree/main/notebooks) directory

## 👑 **Result**

By comparing with last year's results (2024):

1. **Improvement in total stores analyzed:** increased by **321.38%**, from 16.75% of total stores in 2024 to 70.57% in 2025.
2. **Improvement in completion time:** reduced by **77.78%**, from 90 days (3 months) in 2024 to 20 days in 2025.

**Note:** The completion time refers to the duration required to develop the program. For future projects, if the data is already available, the analysis can be completed in **under 7 minutes** by simply running the program.

## 📋 **Dataset**

There are three datasets required for this project:

1. **KM Tempuh Data (Operational Data):** contains information about KM Master and KM Tempuh for each store.
2. **Master Zona Data (Master Data):** contains details about Master Zona, location addresses, and KM Master for each store.
3. **Google Sheet Data:** contains supplementary data used for preprocessing, such as converting Operation Point (OP) names to OP codes and correcting store names that were altered due to Excel’s scientific notation format.

**Note:** For consistency and ease of reference, all column names in this project are presented in the **Indonesian language**.

> **Disclaimer:** Due to data confidentiality, this program operates on the original dataset but **is not publicly displayed**. However, dummy data is provided to illustrate the general structure of the original dataset.
