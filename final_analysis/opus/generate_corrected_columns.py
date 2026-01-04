import pandas as pd
import csv
import os
from glob import glob

# Get raw log data
log_files = glob('/Users/duccioo/Desktop/ai_memory_experiment/ai_experiment/experiment_data/P*-*-*.csv')

raw_sync = {}
raw_summary_viewing = {}

for log_file in sorted(log_files):
    filename = os.path.basename(log_file)
    participant_id = filename.split('-')[0]
    
    if 'Integrated' in filename:
        structure = 'integrated'
    elif 'Segmented' in filename:
        structure = 'segmented'
    else:
        continue
    
    with open(log_file, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            continue
        
        for parts in reader:
            if len(parts) > 1:
                if parts[1] == 'summary_viewing':
                    article = parts[3] if len(parts) > 3 else ''
                    timing = parts[4] if len(parts) > 4 else ''
                    summary_ms = int(parts[6]) if len(parts) > 6 else 0
                    raw_summary_viewing[(participant_id, timing, article)] = summary_ms / 1000
                
                if parts[1] == 'reading_behavior' and len(parts) > 2 and parts[2] == 'reading_complete':
                    reading_time_ms = int(parts[4]) if len(parts) > 4 else 0
                    summary_time_ms = int(parts[5]) if len(parts) > 5 else 0
                    article = parts[9] if len(parts) > 9 else ''
                    timing = parts[10] if len(parts) > 10 else ''
                    
                    if timing:
                        if timing == 'synchronous':
                            reading_corr = (reading_time_ms - summary_time_ms) / 60000
                        else:
                            reading_corr = reading_time_ms / 60000
                        
                        raw_sync[(participant_id, timing, article)] = {
                            'reading_min': reading_corr,
                            'summary_sec': summary_time_ms / 1000
                        }

# Integrated participants
int_participants = ['P233', 'P234', 'P235', 'P236', 'P243', 'P246', 'P251', 'P253', 'P258', 'P260', 'P261', 'P265']
int_reading = []
int_summary = []

for (pid, timing, article), val in raw_sync.items():
    if pid in int_participants and timing == 'synchronous' and pid not in ['P233', 'P236']:
        int_reading.append(val['reading_min'])
        int_summary.append(val['summary_sec'])

int_avg_reading = sum(int_reading) / len(int_reading)
int_avg_summary = sum(int_summary) / len(int_summary)

# Segmented
seg_participants = ['P239', 'P240', 'P241', 'P245', 'P250', 'P252', 'P254', 'P257', 'P259', 'P263', 'P264', 'P266']
seg_reading = []
seg_summary = []

for (pid, timing, article), val in raw_sync.items():
    if pid in seg_participants and timing == 'synchronous':
        seg_reading.append(val['reading_min'])
        seg_summary.append(val['summary_sec'])

seg_avg_reading = sum(seg_reading) / len(seg_reading)
seg_avg_summary = sum(seg_summary) / len(seg_summary)

print(f'Integrated avg (excl P233, P236): reading={int_avg_reading:.2f} min, summary={int_avg_summary:.2f} sec')
print(f'Segmented avg: reading={seg_avg_reading:.2f} min, summary={seg_avg_summary:.2f} sec')
print()

# Excel row order
order = [
    ('P233', 'integrated', 'pre_reading', 'semiconductors'),
    ('P233', 'integrated', 'synchronous', 'crispr'),
    ('P233', 'integrated', 'post_reading', 'uhi'),
    ('P234', 'integrated', 'pre_reading', 'crispr'),
    ('P234', 'integrated', 'synchronous', 'uhi'),
    ('P234', 'integrated', 'post_reading', 'semiconductors'),
    ('P235', 'integrated', 'pre_reading', 'crispr'),
    ('P235', 'integrated', 'synchronous', 'semiconductors'),
    ('P235', 'integrated', 'post_reading', 'uhi'),
    ('P236', 'integrated', 'pre_reading', 'semiconductors'),
    ('P236', 'integrated', 'synchronous', 'uhi'),
    ('P236', 'integrated', 'post_reading', 'crispr'),
    ('P243', 'integrated', 'pre_reading', 'uhi'),
    ('P243', 'integrated', 'synchronous', 'crispr'),
    ('P243', 'integrated', 'post_reading', 'semiconductors'),
    ('P246', 'integrated', 'pre_reading', 'semiconductors'),
    ('P246', 'integrated', 'synchronous', 'uhi'),
    ('P246', 'integrated', 'post_reading', 'crispr'),
    ('P251', 'integrated', 'pre_reading', 'uhi'),
    ('P251', 'integrated', 'synchronous', 'crispr'),
    ('P251', 'integrated', 'post_reading', 'semiconductors'),
    ('P253', 'integrated', 'pre_reading', 'crispr'),
    ('P253', 'integrated', 'synchronous', 'semiconductors'),
    ('P253', 'integrated', 'post_reading', 'uhi'),
    ('P258', 'integrated', 'pre_reading', 'crispr'),
    ('P258', 'integrated', 'synchronous', 'semiconductors'),
    ('P258', 'integrated', 'post_reading', 'uhi'),
    ('P260', 'integrated', 'pre_reading', 'crispr'),
    ('P260', 'integrated', 'synchronous', 'semiconductors'),
    ('P260', 'integrated', 'post_reading', 'uhi'),
    ('P261', 'integrated', 'pre_reading', 'uhi'),
    ('P261', 'integrated', 'synchronous', 'semiconductors'),
    ('P261', 'integrated', 'post_reading', 'crispr'),
    ('P265', 'integrated', 'pre_reading', 'semiconductors'),
    ('P265', 'integrated', 'synchronous', 'crispr'),
    ('P265', 'integrated', 'post_reading', 'uhi'),
    ('P239', 'segmented', 'pre_reading', 'uhi'),
    ('P239', 'segmented', 'synchronous', 'semiconductors'),
    ('P239', 'segmented', 'post_reading', 'crispr'),
    ('P240', 'segmented', 'pre_reading', 'uhi'),
    ('P240', 'segmented', 'synchronous', 'crispr'),
    ('P240', 'segmented', 'post_reading', 'semiconductors'),
    ('P241', 'segmented', 'pre_reading', 'semiconductors'),
    ('P241', 'segmented', 'synchronous', 'crispr'),
    ('P241', 'segmented', 'post_reading', 'uhi'),
    ('P245', 'segmented', 'pre_reading', 'semiconductors'),
    ('P245', 'segmented', 'synchronous', 'uhi'),
    ('P245', 'segmented', 'post_reading', 'crispr'),
    ('P250', 'segmented', 'pre_reading', 'crispr'),
    ('P250', 'segmented', 'synchronous', 'semiconductors'),
    ('P250', 'segmented', 'post_reading', 'uhi'),
    ('P252', 'segmented', 'pre_reading', 'uhi'),
    ('P252', 'segmented', 'synchronous', 'crispr'),
    ('P252', 'segmented', 'post_reading', 'semiconductors'),
    ('P254', 'segmented', 'pre_reading', 'semiconductors'),
    ('P254', 'segmented', 'synchronous', 'crispr'),
    ('P254', 'segmented', 'post_reading', 'uhi'),
    ('P257', 'segmented', 'pre_reading', 'uhi'),
    ('P257', 'segmented', 'synchronous', 'crispr'),
    ('P257', 'segmented', 'post_reading', 'semiconductors'),
    ('P259', 'segmented', 'pre_reading', 'crispr'),
    ('P259', 'segmented', 'synchronous', 'semiconductors'),
    ('P259', 'segmented', 'post_reading', 'uhi'),
    ('P263', 'segmented', 'pre_reading', 'semiconductors'),
    ('P263', 'segmented', 'synchronous', 'crispr'),
    ('P263', 'segmented', 'post_reading', 'uhi'),
    ('P264', 'segmented', 'pre_reading', 'crispr'),
    ('P264', 'segmented', 'synchronous', 'uhi'),
    ('P264', 'segmented', 'post_reading', 'semiconductors'),
    ('P266', 'segmented', 'pre_reading', 'semiconductors'),
    ('P266', 'segmented', 'synchronous', 'uhi'),
    ('P266', 'segmented', 'post_reading', 'crispr'),
]

print('=' * 60)
print('CORRECTED reading_time_min (72 AI rows):')
print('=' * 60)

reading_values = []
summary_values = []

for pid, structure, timing, article in order:
    key = (pid, timing, article)
    
    # Reading time
    if timing == 'synchronous' and pid in ['P233', 'P236']:
        read_val = int_avg_reading
    elif key in raw_sync:
        read_val = raw_sync[key]['reading_min']
    else:
        if structure == 'integrated':
            read_val = int_avg_reading
        else:
            read_val = seg_avg_reading
    
    # Summary time
    if timing == 'synchronous':
        if pid in ['P233', 'P236']:
            sum_val = int_avg_summary
        elif key in raw_sync:
            sum_val = raw_sync[key]['summary_sec']
        else:
            if structure == 'integrated':
                sum_val = int_avg_summary
            else:
                sum_val = seg_avg_summary
    else:
        # For pre/post reading, get from summary_viewing
        if key in raw_summary_viewing:
            sum_val = raw_summary_viewing[key]
        else:
            sum_val = 0  # Should not happen
    
    reading_values.append(round(read_val, 2))
    summary_values.append(round(sum_val, 2))
    print(f'{pid} {timing} {article}: reading={round(read_val, 2)}, summary={round(sum_val, 2)}')

# Calculate new averages
int_sync_indices = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34]
seg_sync_indices = [37, 40, 43, 46, 49, 52, 55, 58, 61, 64, 67, 70]

int_sync_reading = [reading_values[i] for i in int_sync_indices]
seg_sync_reading = [reading_values[i] for i in seg_sync_indices]
int_sync_summary = [summary_values[i] for i in int_sync_indices]
seg_sync_summary = [summary_values[i] for i in seg_sync_indices]

print()
print('=' * 60)
print('NEW AVERAGES:')
print('=' * 60)
print(f'Integrated synchronous reading avg: {sum(int_sync_reading)/len(int_sync_reading):.2f} min')
print(f'Segmented synchronous reading avg: {sum(seg_sync_reading)/len(seg_sync_reading):.2f} min')
print(f'Integrated synchronous summary avg: {sum(int_sync_summary)/len(int_sync_summary):.2f} sec')
print(f'Segmented synchronous summary avg: {sum(seg_sync_summary)/len(seg_sync_summary):.2f} sec')

print()
print('=' * 60)
print('READING_TIME_MIN COLUMN (copy-paste for Excel):')
print('=' * 60)
for v in reading_values:
    print(v)

print()
print('=' * 60)
print('SUMMARY_TIME_SEC COLUMN (copy-paste for Excel):')
print('=' * 60)
for v in summary_values:
    print(v)
