import os
def ShowMainResults(brand_name, similarity, verdict):
    results = []
    print(similarity)
    results.append({
        'brand_name': brand_name,
        'similarity': round(similarity * 100,2),
        'verdict': verdict,
    })

    return results[:1]
