def test_forced_eviction():
    from src.cache.cluster import cluster
    from src.cache.lru_tracker import track_access, evict_oldest
    import time
    
    # Define um limite baixo de memória para o teste (1MB)
    max_memory = 1_000_000
    
    # Insere 10.000 chaves, cada uma com aproximadamente 1KB
    for i in range(10_000):
        key = f"test:{i}"
        cluster.set(key, "x" * 1024)
        track_access(key)
    
    # Aguarda um pouco para garantir a atualização do uso de memória
    time.sleep(2)
    
    # Executa a evicção dos keys mais antigos
    evict_oldest(max_memory)
    
    # Verifica que a memória utilizada foi reduzida abaixo do limite
    current_mem = int(cluster.info("memory")["used_memory"])
    assert current_mem < max_memory, "Memória usada deve ser menor que o máximo definido após evicção" 