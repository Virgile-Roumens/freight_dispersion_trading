# 📁 Engelhart Freight Analytics - Project Structure

## Directory Organization

```
freight_project/
│
├── 📊 data/                        # Datasets
│   ├── cape_front_month.csv        # 5TC FFA prices (2016-2025)
│   └── dispersion_case_study.csv   # Vessel dispersion data
│
├── 🎨 assets/                      # Visual resources
│   ├── engelhart_logo.png          # Primary logo
│   └── logo.jpg                    # Alternative logo
│
├── 📤 export/                      # Backtest results (auto-generated)
│   └── [backtest_*.xlsx/csv]       # Exported performance reports
│
├── 📚 docs_archive/                # Historical documentation
│   ├── SIGNAL_EXPLANATION.md
│   ├── STRATEGY_ADAPTATION.md
│   ├── USAGE_GUIDE_ADAPTED.md
│   ├── USER_GUIDE.md
│   └── UX_IMPROVEMENTS.md
│
├── 🐍 Core Application Files
│   ├── streamlit_app.py            # Main dashboard (1,691 lines)
│   ├── data_manager.py             # Data loading & validation
│   ├── signal_generator.py         # Trading signal generation
│   └── backtest_engine.py          # Portfolio simulation & metrics
│
├── 📖 Documentation
│   ├── README.md                   # Complete project guide ⭐
│   ├── ENGELHART_DESIGN_SYSTEM.md  # Brand guidelines (6,000+ words)
│   ├── PERFORMANCE_METRICS_UPGRADE.md  # FRED API integration
│   └── ARCHITECTURE_QUICK_REF.py   # Code architecture
│
├── ⚙️ Configuration
│   ├── requirements.txt            # Python dependencies
│   ├── .gitignore                  # Git exclusions
│   └── organize_files.ps1          # Setup script
│
└── 🗂️ System
    └── __pycache__/                # Python bytecode cache
```

## Key Files Reference

### Core Application (Python)

| File | Lines | Purpose |
|------|-------|---------|
| `streamlit_app.py` | 1,691 | Main Streamlit dashboard with 3 tabs |
| `backtest_engine.py` | ~500 | Portfolio simulation, FRED API, metrics |
| `signal_generator.py` | ~400 | Momentum signals, filters, explanations |
| `data_manager.py` | ~300 | CSV loading, validation, quality checks |

### Documentation

| File | Size | Purpose |
|------|------|---------|
| `README.md` | 10KB | **Primary documentation** - installation, usage, features |
| `ENGELHART_DESIGN_SYSTEM.md` | 25KB | Complete brand guidelines |
| `PERFORMANCE_METRICS_UPGRADE.md` | 8KB | FRED API & metrics documentation |
| `ARCHITECTURE_QUICK_REF.py` | 3KB | Code architecture overview |

### Data Files

| File | Rows | Columns | Period |
|------|------|---------|--------|
| `data/cape_front_month.csv` | ~2,300 | 2 | 2016-2025 |
| `data/dispersion_case_study.csv` | ~2,300 | 7 | 2016-2025 |

**Columns in dispersion CSV:**
- `date`
- `cape_dispersion`
- `cape_vessel_count`
- `vloc_dispersion`
- `vloc_vessel_count`
- `avg_dispersion` (weighted)
- `total_vessel_count`

## File Paths in Code

All code now uses organized paths:

```python
# Data loading (streamlit_app.py)
DataManager(
    price_csv='data/cape_front_month.csv',
    dispersion_csv='data/dispersion_case_study.csv'
)

# Logo display (streamlit_app.py)
st.image('assets/engelhart_logo.png')

# Export location (backtest_engine.py)
export_path = Path('export') / filename
```

## Quick Start Commands

```bash
# Navigate to project
cd "c:\Users\Virgile ROUMENS\Desktop\Engelhart\freight_project"

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run streamlit_app.py

# View exports
cd export
```

## Git Status

Current `.gitignore` excludes:
- ✅ `__pycache__/` - Python bytecode
- ✅ `export/` - Generated backtest results
- ✅ `docs_archive/` - Old documentation
- ✅ `.vscode/`, `.idea/` - IDE files
- ⚠️ `data/*.csv` - **Currently tracked** (uncomment in .gitignore if datasets are large)

## Maintenance

### Adding New Data
```bash
# Place new CSV files in data/
cp new_data.csv data/

# Update paths in code if needed
```

### Updating Branding
```bash
# Replace logo in assets/
cp new_logo.png assets/engelhart_logo.png

# No code changes needed (paths are relative)
```

### Exporting Results
- Results automatically save to `export/` folder
- Filename includes parameters: `backtest_lag{X}_capital{Y}k_fees{Z}bps_YYYYMMDD_HHMM`
- Format: Excel (.xlsx) or CSV (3 files)

---

**Last Updated:** December 18, 2025  
**Organization Status:** ✅ Complete
