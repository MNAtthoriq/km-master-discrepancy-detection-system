# **KM Master Discrepancy Detection System**

![Python Code](https://img.shields.io/badge/Python-Code-blue?logo=python&logoColor=white)
![Sheets API](https://img.shields.io/badge/Google_Sheets-API-34A853?logo=googlesheets&logoColor=white)

A systematic framework to identify and prioritize discrepancies in KM Master (transportation distance) data. This system provides **KM Master recommendations** for each store, enabling operations teams to efficiently **prioritize** which KM Master data should be validated.

## 🎯 **Problem**

KM Master represents the round-trip distance between an Operating Point (OP) and a Store. It's **critical** for calculating *Uang Jalan Pengiriman* or **UJP** (transportation costs).

An inaccurate KM Master can lead to **significant issues**:
- **Underestimated distances** → Operational problems, driver dissatisfaction
- **Overestimated distances** → Fraud opportunities, inflated costs

With **thousands of stores**, manually validating all KM Master entries is impractical. The operations team needs to **prioritize** which entries to validate first.

## 💡 **Solution**

A rule-based recommendation system applying three methods in priority order:

1. **KM Master Method** - Identifies anomalous value based on operational knowledges
2. **KM Tempuh Method** - Uses historical KM Tempuh (delivery distance) averages
3. **Master Zona Method** - Applies UJP zone-based recommendations

If a recommendation is available from a higher-priority method (e.g, KM Master), the lower-priority methods (e.g, KM Tempuh) will be ignored.

## 📊 **Result**

Compared to 2024's manual approach:

| Metric | 2024 | 2025 | Improvement |
|:--------|------:|------:|-------------:|
| **Stores Analyzed** | 16.75% | 70.57% | **+321.38%** |
| **Completion Time** | 90 days | 20 days | **-77.78%** |
| **Future Runtime** | N/A | <7 minutes | **Instant** |

## 📋 **Dataset**

There are three datasets required for this project:

1. **Google Sheet Data**
    - Sheet `Master Kode OP` - used for data preprocessing
    - Sheet `Master Saintifik Toko` - used for data preprocessing
    - Sheet `Rekomendasi KM Master` - used in **KM Master Method**
2. **Operational Data:**
    - Columns: `OP`, `Toko`, `KM Tempuh`, `KM Master`, `KM Max`
    - Used mainly in **KM Tempuh Method**
2. **Master Zona Data:**
    - Columns: `OP`, `Toko`, `KM Master`, `Kode Zona`, `Provinsi`, `Status Toko`
    - Used in **Master Zona Method**

**Note**: Column names are in Indonesian to match source systems.

> **Disclaimer:** Due to confidentiality, actual data is not included in this repository. Dummy data structure is provided for reference.

## 📁 **Architecture**
```
km-master-discrepancy-detection-system/
├── src/
│   ├── __init__.py
│   ├── config.py               # Centralized configuration
│   ├── google_sheets_io.py     # Google Sheets API integration
│   ├── data_preprocessing.py   # Data preprocessing functions
│   └── utils.py                # Logger and helper functions
├── notebooks/
│   └── 01-KM-Master-Discrepancy-Detection.ipynb
├── data/
│   └── .gitkeep                # Data folder (files not included)
├── logs/
│   └── .gitkeep                # Log files
├── requirements.txt
├── .gitignore
├── LICENSE
└── README.md
```

## 🚀 **Quick Start**

### **Prerequisites**
```bash
# Python 3.8+
python --version

# Install dependencies
pip install -r requirements.txt
```

### **Setup**

1. **Clone Repo**
    ```bash
    git clone https://github.com/MNAtthoriq/km-master-discrepancy-detection-system.git
    cd km-master-discrepancy-detection-system
    ```

2. **Configure Credentials**

    Create `.env` file (Google Sheets URL for data):
    ```env
    !add later
    ```

    Add `credentials.json` (Google Service Account for Google Sheet API):
    ```json
    {
      "type": "service_account",
      "project_id": "your-project",
      "private_key_id": "...",
      "private_key": "...",
      "client_email": "...",
      ...
    }
    ```

3. **Prepare Data**

    Place .CSV data files in `data/` directory:
    ```
    data/
    ├── 1. Operational Data - Januari 2025.csv
    ├── 2. Operational Data - Februari 2025.csv
    ...
    └── Master Zona Data.csv
    ```

### **Usage**

```python
# In Jupyter Notebook
import sys
sys.path.append('../src')

from data_loader import sheets_loader
from data_cleaning import op_code, change_scientific_notation
from utils import setup_logging

# Setup logging
setup_logging(log_file='../logs/analysis.log') # Change to your desired path

# Run your analysis
# (See notebook for complete workflow)
```

## 🤝 **Contributing**

This is a personal portfolio project, but suggestions and feedback are welcome! 

Please open an issue for discussion.

## 👤 **Author**

**Muhammad Naufal At-Thoriq**
- GitHub: [MNAtthoriq](https://github.com/MNAtthoriq)
- LinkedIn: [Muhammad Naufal At-Thoriq](https://linkedin.com/in/mnatthoriq)

---

⭐ **If this project helps you, please star it on GitHub!**
