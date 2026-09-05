# Deadlock Match Win Probability Predictor

Real-time machine learning system for predicting Deadlock match win probabilities, with a live in-game overlay.

## Overview

Deadlock Match Win Probability Predictor is an end-to-end machine learning project that estimates the probability of a team winning a Deadlock match from the current game state.

The system contains:

- Historical match data for model training
- Feature engineering over player-level and team-level statistics
- XGBoost, CatBoost were used for the final ensemble model
- Separate models for different stages of a match
- A Rust-based live event server
- A Python live prediction script
- A PySide6 in-game overlay
- A standalone Windows launcher

The project is designed to run a complete live application rather than only offline ML Experiments.

## Features

- **Real-time predictions** from live match data
- **Time-specific pre-trained models** for 5, 10, 15, 20, 25, 30, 35, and 40 minutes.
- **XGBoost and CatBoost ensemble** for final prediction
- **Feature engineering** using team economy, combat, objectives, heroes, lane assignment, and individual player-related statistics.
- **In-game overlay** displaying every minute's current win probability
- **Standalone Windows release** with compiled application components and a simple launcher
- **No Python or Rust installation required** when using compiled release

## Demo

### In-game overlay

The overlay displays the current estimated win probability and the game time, with additional info about the model used for prediction.

### Launcher

![Launcher](screenshots/launcher.png)

The launcher accepts a match ID and starts the required application components.

## How it works

The system has two main pipelines: an offline training pipeline and a live prediction pipeline.

![Architecture](screenshots/architecture.svg)

### Offline training pipeline

Historical match metadata is collected through the Deadlock API and stored as individual JSON files. The preprocessing script extracts snapshots from the match timeline data and creates match-level datasets containing both teams and the winner label.

The training pipeline then loads a snapshot dataset, builds team- and player-level features, and engineers additional features. XGBoost and CatBoost models are then trained and combined into a final ensemble model, which is then saved with feature-column definitions for live inference.

