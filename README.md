# Life Insurance Renewal Premium Collection Forecasting

## Overview

This project analyzes and forecasts renewal premium collections for life
insurance companies.

Renewal premium is the recurring premium collected from existing insurance
policies. The project studies how renewal collections change over time
across insurers, policy duration buckets, payment modes and other
business dimensions.

The system combines data analysis, time-series forecasting and an
interactive Streamlit dashboard.

---

## Problem Statement

Renewal premium collection can vary across months, insurers, policy
durations and payment modes.

Understanding these historical patterns helps insurers analyze recurring
premium income and forecast future renewal collections.

---

## Objectives

- Consolidate historical monthly renewal premium collection.
- Analyze renewal trends over time.
- Analyze premium collection across insurers.
- Analyze policy duration buckets.
- Analyze payment mode distribution.
- Build baseline and time-series forecasting models.
- Compare forecasting models using multiple error metrics.
- Perform time-ordered backtesting.
- Forecast future renewal premium collections.
- Present the results through an interactive Streamlit dashboard.

---

## Tech Stack

- Python
- pandas
- NumPy
- statsmodels
- Prophet
- Streamlit
- Matplotlib
- Plotly

---

## Dataset

The project uses historical insurance renewal data containing information
such as:

- Policy ID
- Collection Date
- Insurer
- Premium Amount
- Payment Mode
- Policy Duration
- Policy Type
- Customer Age
- Region
- Renewal Status

The data is cleaned and transformed before analysis and forecasting.

---

## Project Workflow

```text
Raw Insurance Data
        ↓
Data Cleaning & Preprocessing
        ↓
Monthly Aggregation
        ↓
Exploratory Analysis
        ↓
Trend / Seasonality Analysis
        ↓
Duration Bucket Analysis
        ↓
Payment Mode Analysis
        ↓
Stationarity Analysis
        ↓
Model Training
        ↓
Time-Ordered Backtesting
        ↓
Model Comparison
        ↓
Future Forecasting
        ↓
Streamlit Dashboard