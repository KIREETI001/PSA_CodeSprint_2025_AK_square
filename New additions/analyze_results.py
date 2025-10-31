import pandas as pd

df = pd.read_csv('data/output.csv')
df['duration'] = df['end_time'] - df['start_time']

print('=== OVERALL METRICS ===')
print(f'Total jobs: {len(df)}')
print(f'Makespan: {df["end_time"].max():,} seconds')
print(f'Average duration: {df["duration"].mean():.1f}s')

print('\n=== BY JOB TYPE ===')
stats = df.groupby('job_type')['duration'].agg(['count', 'mean', 'std', 'min', 'max']).round(1)
print(stats)

print('\n=== QC COMPLETION TIMES ===')
qc_end = df.groupby('QC_name')['end_time'].max().sort_values()
for qc, time in qc_end.items():
    print(f'{qc}: {time:,}s')
print(f'\nQC imbalance: {qc_end.max() - qc_end.min():,}s')

print('\n=== YARD UTILIZATION (DI jobs only) ===')
yard_counts = df[df['job_type']=='DI'].groupby('assigned_yard_name').size().sort_values()
print(yard_counts)
print(f'\nYard imbalance: {yard_counts.max() - yard_counts.min()} jobs')

print('\n=== PATH ANALYSIS ===')
# Estimate travel time saved if we could optimize paths
# Current: ~235-337 sectors per job, potential: ~100-150 sectors
current_avg_sectors = 280
optimal_avg_sectors = 125
jobs_count = len(df)
time_per_sector = 10
potential_savings = (current_avg_sectors - optimal_avg_sectors) * time_per_sector * jobs_count
print(f'Current avg path length: ~{current_avg_sectors} sectors')
print(f'Optimal avg path length: ~{optimal_avg_sectors} sectors')
print(f'Potential time savings: {potential_savings:,} seconds ({potential_savings/60/60:.1f} hours)')
print(f'Target makespan: 1,000,000s')
print(f'Current makespan: {df["end_time"].max():,}s')
print(f'Gap to target: {df["end_time"].max() - 1000000:,}s ({(df["end_time"].max() / 1000000 - 1) * 100:.1f}% over)')
