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

For detailed explanation, go to [src](https://github.com/MNAtthoriq/km-master-discrepancy-detection-system/tree/main/src) directory