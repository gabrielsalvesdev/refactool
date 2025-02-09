def test_cluster_slot_distribution():
    from src.cache.cluster import cluster
    slots_info = cluster.cluster("slots")
    # Verifica que há pelo menos 3 slots (representando 3 masters)
    assert len(slots_info) >= 3, "Deve haver pelo menos 3 masters no cluster"
    
    # Para cada range, verifica que o início é menor ou igual ao fim
    for slot in slots_info:
        # Assumindo que cada slot é representado como [start, end, master, ...]
        start, end = slot[0], slot[1]
        assert start <= end, f"Range inválido: start {start} > end {end}" 