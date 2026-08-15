# Phase 1 Data Pipeline Verification Script
import os
import sys

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure data package is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.primus_loader import PrIMuSDataset

def run_phase1_demo():
    print("=" * 60)
    print("PHASE 1 FOUNDATIONS - PrIMuS DATA PIPELINE VERIFICATION")
    print("=" * 60)
    
    # 1. Instantiate PrIMuS Dataset (Agnostic sequence mode)
    dataset_agnostic = PrIMuSDataset(data_dir="data/primus", annotation_type="agnostic", sample_count=10)
    
    # 2. Instantiate PrIMuS Dataset (Semantic sequence mode)
    dataset_semantic = PrIMuSDataset(data_dir="data/primus", annotation_type="semantic", sample_count=10)
    
    print("\n--- SAMPLE 1 VERIFICATION (Agnostic Representation) ---")
    img_agnostic, token_ids_agnostic, raw_tokens_agnostic = dataset_agnostic[0]
    print(f"Image Size: {img_agnostic.size}")
    print(f"Raw Agnostic Tokens ({len(raw_tokens_agnostic)}): {raw_tokens_agnostic}")
    print(f"Encoded Token IDs ({len(token_ids_agnostic)}): {token_ids_agnostic.tolist()}")
    
    decoded_agnostic = dataset_agnostic.vocab.decode(token_ids_agnostic.tolist())
    print(f"Decoded Tokens: {decoded_agnostic}")
    assert raw_tokens_agnostic == decoded_agnostic, "Error: Token encoding/decoding mismatch!"
    print("OK: Agnostic Token Alignment Verified!")

    print("\n--- SAMPLE 1 VERIFICATION (Semantic Representation) ---")
    img_semantic, token_ids_semantic, raw_tokens_semantic = dataset_semantic[0]
    print(f"Raw Semantic Tokens ({len(raw_tokens_semantic)}): {raw_tokens_semantic}")
    print(f"Encoded Token IDs ({len(token_ids_semantic)}): {token_ids_semantic.tolist()}")
    
    decoded_semantic = dataset_semantic.vocab.decode(token_ids_semantic.tolist())
    print(f"Decoded Tokens: {decoded_semantic}")
    assert raw_tokens_semantic == decoded_semantic, "Error: Token encoding/decoding mismatch!"
    print("OK: Semantic Token Alignment Verified!")
    
    print("\n" + "=" * 60)
    print("OK: PHASE 1 DATA PIPELINE VERIFICATION COMPLETE & SUCCESSFUL!")
    print("=" * 60)

if __name__ == "__main__":
    run_phase1_demo()
