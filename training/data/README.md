Historical match data is collected from the Deadlock API and stored locally as raw JSON match metadata.

The collection script requests recently fetched matches, retrieves their metadata, skips matches already stored locally, and uses concurrent requests to accelerate collection.

The preprocessing pipeline converts the raw metadata into match-level snapshot datasets. Each row represents both teams at a selected point in the match and contains the eventual winning-team label.

Raw match metadata is stored locally as individual JSON files and is not included in the repository because I have collected over 75GB of data( >20.500 matches)

The dataset and processed CSV files can be reproduced using the scripts in ['data_collection/'](data_collection/)
