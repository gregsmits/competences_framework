

def spearman_correlation(res1: dict[str, float], res2: dict[str, float]) -> float:
    """Compare two sets of resources based on their degrees of relevance using Spearman's rank correlation coefficient.

    Args:
        res1 (Resource): _description_
        res2 (Resource): _description_

    Returns:
        float: A similarity score between 0 and 1.
    """
    #Ensure both resource dicts have the same keys
    common_keys = set(res1.keys()).intersection(set(res2.keys()))
    if len(common_keys) == 0:
        return 0.0  #No common resources to compare

    #Extract the degrees for the common resources
    degrees1 = [res1[k] for k in common_keys]
    degrees2 = [res2[k] for k in common_keys]
    #Compute Spearman's rank correlation coefficient
    n = len(common_keys)
    rank_diff_sum = sum((rank1 - rank2) ** 2 for rank1, rank2 in zip(degrees1, degrees2))
    if n <= 1:
        return 0.0
    spearman_coeff = 1 - (6 * rank_diff_sum) / (n * (n**2 - 1))
    return spearman_coeff

def raw_differences(res1: dict[str, float], res2: dict[str, float]) -> dict[str, float]:
    """Compute raw differences between two resource degree dictionaries.

    Args:
        res1 (dict[str, float]): _description_
        res2 (dict[str, float]): _description_

    Returns:
        dict[str, float]: A dictionary with resource IDs as keys and degree differences as values.
    """
    differences = {}
    common_keys = set(res1.keys()).intersection(set(res2.keys()))
    for key in common_keys:
        differences[key] = res1[key] - res2[key]
    return differences


if __name__ == "__main__":
    #Test the comparator
    res_a = {"res1": 3.0, "res2": 1.0, "res3": 2.0}
    res_b = {"res1": 1.0, "res2": 3.0, "res3": 2.0}
    score = spearman_correlation(res_a, res_b)
    print(f"Spearman correlation score: {score}")