import hashlib

def regenerate_seed_history(initial_password, iterations):
    """Regenera o histórico do seed desde o início"""
    current_seed = initial_password
    for i in range(iterations):
        current_seed = hashlib.sha256(current_seed.encode()).hexdigest()
    return current_seed

def generate_zip_password(timestamp, seed):
    """Gera a password para um ZIP específico"""
    # Algoritmo: SHA256(str(seed + timestamp))
    data = str(seed + str(timestamp)).encode('utf-8')
    return hashlib.sha256(data).hexdigest()

# Configuração
INITIAL_PASSWORD = "TheByteOf78"

backups = [
    ("1758495226", 69),  
    ("1758585623", 70),  
    ("1758586202", 71),  
    ("1758586801", 72),    
    ("1758587401", 73),  
    ("1758588001", 74),  
    ("1758588601", 75),  
    ("1758589201", 76),  
]

print("=== TESTANDO DIFERENTES ITERAÇÕES ===")

for timestamp, base_iteration in backups:
    print(f"\nTimestamp: {timestamp}")
    
    # Testar iterações próximas
    for offset in [-3, -2, -1, 0, 1, 2, 3]:
        test_iteration = base_iteration + offset
        if test_iteration >= 0:
            seed_used = regenerate_seed_history(INITIAL_PASSWORD, test_iteration)
            password = generate_zip_password(timestamp, seed_used)
            
            print(f"  Iteração {test_iteration}: {password}")
