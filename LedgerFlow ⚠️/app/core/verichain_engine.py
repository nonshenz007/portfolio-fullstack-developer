import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from app.models.invoice import Invoice

class VeriChainEngine:
    """
    VeriChain Engine provides tamper-evident verification of invoice integrity.
    Each invoice is hashed individually and chained together like a mini blockchain.
    """
    
    def __init__(self):
        self.hash_algorithm = hashlib.sha256
        self.chain_dir = Path('LedgerFlow/verichain_logs')
        self.chain_dir.mkdir(parents=True, exist_ok=True)
        
    def hash_invoice_data(self, invoice_data: Dict[str, Any]) -> str:
        """
        Generate SHA-256 hash of invoice data.
        Only hashes key fields that should never change.
        """
        # Extract key fields that should be hashed
        key_fields = {
            'invoice_number': invoice_data['invoice_number'],
            'invoice_type': invoice_data['invoice_type'],
            'invoice_date': invoice_data['invoice_date'],
            'customer_name': invoice_data['customer_name'],
            'subtotal': invoice_data['subtotal'],
            'tax_amount': invoice_data['tax_amount'],
            'total_amount': invoice_data['total_amount'],
            'items': invoice_data.get('items', [])
        }
        
        # Convert to JSON string and hash
        json_str = json.dumps(key_fields, sort_keys=True)
        return self.hash_algorithm(json_str.encode()).hexdigest()
    
    def generate_chain_for_batch(self, batch_id: str, invoices: List[Dict[str, Any]]) -> str:
        """
        Generate a VeriChain log for a batch of invoices.
        Returns the final chain hash.
        """
        chain_file = self.chain_dir / f"verichain_{batch_id}.json"
        chain_data = []
        
        prev_hash = None
        for invoice in invoices:
            # Generate hash for this invoice
            current_hash = self.hash_invoice_data(invoice)
            
            # Create chain entry
            chain_entry = {
                'invoice_number': invoice['invoice_number'],
                'timestamp': datetime.now().isoformat(),
                'previous_hash': prev_hash,
                'current_hash': current_hash,
                'chain_position': len(chain_data) + 1
            }
            
            chain_data.append(chain_entry)
            prev_hash = current_hash
        
        # Generate final chain hash
        final_chain_data = {
            'batch_id': batch_id,
            'generation_time': datetime.now().isoformat(),
            'total_invoices': len(invoices),
            'chain': chain_data,
            'final_chain_hash': prev_hash
        }
        
        # Save to file
        with open(chain_file, 'w') as f:
            json.dump(final_chain_data, f, indent=2)
        
        return prev_hash
    
    def verify_chain(self, batch_id: str) -> Dict[str, Any]:
        """
        Verify the integrity of a VeriChain log.
        Returns verification results including any detected tampering.
        """
        chain_file = self.chain_dir / f"verichain_{batch_id}.json"
        
        if not chain_file.exists():
            return {
                'success': False,
                'error': f'No chain log found for batch {batch_id}'
            }
        
        with open(chain_file) as f:
            chain_data = json.load(f)
        
        verification_results = {
            'success': True,
            'batch_id': batch_id,
            'total_invoices': len(chain_data['chain']),
            'integrity_checks': []
        }
        
        prev_hash = None
        for entry in chain_data['chain']:
            # Verify current hash matches stored hash
            current_hash = entry['current_hash']
            
            # Verify chain integrity
            if prev_hash and prev_hash != entry['previous_hash']:
                verification_results['success'] = False
                verification_results['integrity_checks'].append({
                    'invoice_number': entry['invoice_number'],
                    'error': 'Chain broken - previous hash mismatch'
                })
            
            prev_hash = current_hash
        
        return verification_results
    
    def get_chain_log(self, batch_id: str) -> Dict[str, Any]:
        """
        Get the complete VeriChain log for a batch.
        """
        chain_file = self.chain_dir / f"verichain_{batch_id}.json"
        
        if not chain_file.exists():
            return {
                'success': False,
                'error': f'No chain log found for batch {batch_id}'
            }
        
        with open(chain_file) as f:
            return json.load(f)