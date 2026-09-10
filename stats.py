#statistical anomaly checks - needs historical data unlike tools.py

import statistics

def calculate_column_stats(values: list[float]) -> dict:
    if len(values)<2:
        return None
    mean=statistics.mean(values)
    std_dev=statistics.stdev(values)

    sorted_values=sorted(values)
    q1=statistics.quantiles(sorted_values, n=4)[0]
    q3=statistics.quantiles(sorted_values, n=4)[2]
    iqr=q3-q1

    return {
        "mean":mean,
        "std_dev": std_dev,
        "q1":q1,
        "q3":q3,
        "iqr":iqr,
        "lower_bound":q1-1.5*iqr,
        "upper_bound":q3+1.5*iqr
    }

def check_zscore(value: float, stats:dict, threshold: float=3.0) -> str | None:
    if stats is None or stats["std_dev"]==0:
        return None

    z=(value-stats["mean"])/stats["std_dev"]

    if abs(z)>threshold:
        return f"Vlaue {value} has z-score of {z:.2f} (mean={stats['mean']:.2f}, std_dev={stats['std_dev']:.2f}) unusually far from normal"
    return None

def check_iqr(value: float, stats:dict) -> str | None:
    if stats is None:
        return None

    if value<stats["lower_bound"] or value>stats["upper_bound"]:
        return f"Value {value} is outside the expected range ({stats['lower_bound']:.2f} to {stats['upper_bound']:.2f})"
    return None