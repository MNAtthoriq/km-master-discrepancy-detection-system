# **KM Master Discrepancy Detection System**

![Python Code](https://img.shields.io/badge/Python-Code-blue?logo=python&logoColor=white)
![Sheets API](https://img.shields.io/badge/Google_Sheets-API-34A853?logo=googlesheets&logoColor=white)

A systematic framework to identify and prioritize discrepancies in KM Master data. This system enables the operations team to efficiently determine and prioritize which KM Master data entries should be validated for each store.

## 🎯 **Problem**

The KM Master data represents the round-trip distance between an Operating Point and a Store. It serves as a crucial reference for determining transportation costs (*Uang Jalan Pengiriman* or **UJP**).

An inaccurate KM Master can lead to significant problems: **underestimated distances** may cause operational problems, while **overestimated distances** may create opportunities for frauds. Therefore, it requires regular validation to ensure accuracy.

However, manually validating all thousands of KM Master entries for each store is highly inefficient. As a result, the operations team must prioritize which KM Master data should be validated first.

## 💡 **Solution**

A rule-based framework that used three methods:
1. **KM Master Method**
2. **KM Tempuh Method**
3. **Master Zona Method**