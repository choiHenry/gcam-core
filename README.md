# High Ambition Korea 2035 – A Package for Replication

This repository contains the model implementation, scenario configuration, and result analysis code accompanying:

> Choi, H., Park, S., & McJeon, H. *High-ambition climate action in all sectors can achieve a 60% greenhouse gas emissions reduction in Korea by 2035*. [Working Paper / Preprint link]

## Contact
- **Hyuntae Choi** – [chti0265@snu.ac.kr](mailto:chti0265@snu.ac.kr)  
- **Haewon McJeon** – [hmcjeon@kaist.ac.kr](mailto:hmcjeon@kaist.ac.kr)  
- **Sangin Park** – [sanpark@snu.ac.kr](mailto:sanpark@snu.ac.kr)  

---

## Repository Structure

| Directory / File | Description |
|------------------|-------------|
| `policy-implementation/` | Python notebooks by sector for implementing policy inputs |
| ├─ `resources/` | Data used for policy implementation |
| `exe/` | Scenario configuration files for GCAM model runs |
| ├─ `configuration_current_policies_med.xml` | Main configuration for the *Current Policies* scenario |
| ├─ `configuration_enhanced_ambition_med.xml` | Main configuration for the *Enhanced Ambition* scenario |
| `input/policy/korea-2035/` | Policy input files by sector |
| `analysis/` | Python notebooks for analyzing results |
| ├─ `extdata/` | Data used in analysis |

---

## Prerequisites

- **Microsoft Excel** – Required for replicating some policy implementations in `policy-implementation`
- **Python 3.9.23** – Virtual environment recommended (see `requirements.txt` for dependencies)
- **[GCAM v7.1](https://github.com/JGCRI/gcam-core/releases)** – Base model for GCAM-ROK

---

## Installation & Usage

### 1. Install GCAM v7.1

Download [GCAM v7.1](https://github.com/JGCRI/gcam-core/releases) and install it in a directory separate from this repository.  
Reference installation guides:  
- [Windows](https://www.youtube.com/watch?v=2Tv-5rryhk8) – P. Patel  
- [MacOS](https://www.youtube.com/watch?v=AQnm_qZmypA) – P. Patel  
- [GCAM Build Instructions for Linux](https://jgcri.github.io/gcam-doc/gcam-build.html)

---

### 2. Attach Policy Input Files

- Copy the `./input/policy/korea-2035/` folder into the `input` folder of your GCAM installation.
- Download `N_Fert_reduction.xml` [here](https://www.dropbox.com/scl/fi/0qzk3bwc2egfe91wqy2zg/N_Fert_reduction.xml?rlkey=4t33sq0wu3k1o15us5swfhopm&st=a4u14ab6&dl=0) and place it in: `input/gcamdata/xml/`

### 3. Run Scenarios

Navigate to the `exe` directory in your GCAM v7.1 installation.

Example (Windows PowerShell):

```powershell
.\gcam.exe -C configuration_current_policies_med.xml
.\gcam.exe -C configuration_enhanced_ambition_med.xml
```

Example (Linux/Mac):
```bash
./gcam -C configuration_current_policies_med.xml
./gcam -C configuration_enhanced_ambition_med.xml
```

### 4. Analyze Results

1. Set up Python environment:

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Open and run notebooks in `analysis`:
```bash
jupyter notebook analysis/
```

## Citation
If you use this package in your work, please cite:
```text
Choi, H., Park, S., & McJeon, H. (2025).
High-ambition climate action in all sectors can achieve a 60% greenhouse gas emissions reduction in Korea by 2035. Working Paper.
[Preprint link or DOI]
```

## License
[MIT License](https://opensource.org/licenses/MIT) – You are free to use, modify, and distribute this code with attribution.