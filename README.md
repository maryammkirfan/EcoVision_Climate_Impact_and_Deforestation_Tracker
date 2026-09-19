# 🌍 EcoVision — AI-Powered Environmental Monitoring

> **Turning satellite imagery into actionable land-cover intelligence.**

EcoVision is an AI-powered satellite image classification application designed to identify land-cover categories from satellite imagery.

The project combines **deep learning, transfer learning, computer vision, and Streamlit** to provide an interactive interface for environmental monitoring, land-use analysis, and deforestation-related exploration.

## 🚀 Live Demo

**Try EcoVision:**  
[Open the Live App](https://ecovisionclimateimpactanddeforestationtracker.streamlit.app/)

The application is deployed using **Streamlit Community Cloud** and connected directly to this GitHub repository.

---

## 📌 Project Overview

Environmental monitoring increasingly depends on large amounts of satellite imagery.

Manually analyzing this imagery is time-consuming and difficult to scale. EcoVision explores how deep learning can transform satellite image patches into automated land-cover predictions.

The application accepts a satellite image and uses a trained image-classification model to predict its land-cover category.

### Core workflow

```text
Satellite Image
       │
       ▼
 Image Upload
       │
       ▼
 Image Preprocessing
       │
       ▼
 Transfer-Learning Model
       │
       ▼
 Land-Cover Prediction
       │
       ▼
 Predicted Category
