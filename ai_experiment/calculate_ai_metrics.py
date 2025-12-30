import pandas as pd
import numpy as np
import os
from pathlib import Path
import csv

# Get the directory where this script is located
script_dir = Path(__file__).parent
data_dir = script_dir / 'experiment_data'

# Read condition assignments
conditions = pd.read_csv(data_dir / 'condition_assignments.csv')

# Initialize lists to store results
integrated_trust = []
integrated_dependence = []
segmented_trust = []
segmented_dependence = []

# Process each participant
for file in os.listdir(data_dir):
    if file.endswith('_log.csv'):
        participant_id = file.split('-')[0]
        
        try:
            # Open and read with csv module which handles quoted fields properly
            with open(data_dir / file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                
                for row in reader:
                    if len(row) > 1 and row[1] == 'ai_trust':
                        # Get condition for this participant
                        condition_row = conditions[conditions['participantId'] == participant_id]
                        
                        if not condition_row.empty:
                            condition = condition_row['structureCondition'].values[0]
                            
                            # Trust score should be in position 2 (third column, index 2)
                            trust = float(row[2])
                            
                            # Dependence score should be in position 4 (fifth column, index 4)
                            dependence = float(row[4])
                            
                            # Store based on condition
                            if 'Integrated' in condition:
                                integrated_trust.append(trust)
                                integrated_dependence.append(dependence)
                            else:
                                segmented_trust.append(trust)
                                segmented_dependence.append(dependence)
                            
                            break
        except Exception as e:
            print(f"Error processing {participant_id}: {e}")
            continue

# Calculate statistics
print("=" * 60)
print("AI TRUST AND DEPENDENCE ANALYSIS")
print("=" * 60)
print()

print("INTEGRATED CONDITION:")
print(f"  AI Trust:")
print(f"    Mean: {np.mean(integrated_trust):.2f}/7")
print(f"    SD: {np.std(integrated_trust, ddof=1):.2f}")
print(f"    N: {len(integrated_trust)}")
print()
print(f"  AI Dependence:")
print(f"    Mean: {np.mean(integrated_dependence):.2f}/7")
print(f"    SD: {np.std(integrated_dependence, ddof=1):.2f}")
print(f"    N: {len(integrated_dependence)}")
print()

print("SEGMENTED CONDITION:")
print(f"  AI Trust:")
print(f"    Mean: {np.mean(segmented_trust):.2f}/7")
print(f"    SD: {np.std(segmented_trust, ddof=1):.2f}")
print(f"    N: {len(segmented_trust)}")
print()
print(f"  AI Dependence:")
print(f"    Mean: {np.mean(segmented_dependence):.2f}/7")
print(f"    SD: {np.std(segmented_dependence, ddof=1):.2f}")
print(f"    N: {len(segmented_dependence)}")
print()

print("=" * 60)
print("RAW DATA:")
print(f"Integrated Trust: {integrated_trust}")
print(f"Integrated Dependence: {integrated_dependence}")
print(f"Segmented Trust: {segmented_trust}")
print(f"Segmented Dependence: {segmented_dependence}")
