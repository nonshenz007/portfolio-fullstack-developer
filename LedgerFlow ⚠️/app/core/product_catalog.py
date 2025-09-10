import random
from typing import List, Dict, Any

class ProductCatalog:
    """
    In-memory, validated product list for simulation.
    """
    def __init__(self, products: List[Dict[str, Any]]):
        self.products = [p for p in products if self._is_valid(p)]

    def _is_valid(self, product: Dict[str, Any]) -> bool:
        return all(product.get(k) not in [None, '', float('nan')] for k in ['Product Name', 'SKU/HSN', 'Qty', 'Base Rate'])

    def sample_products(self, n: int) -> List[Dict[str, Any]]:
        return random.sample(self.products, min(n, len(self.products)))

    def get_by_sku(self, sku: str) -> Dict[str, Any]:
        for p in self.products:
            if p.get('SKU/HSN') == sku:
                return p
        return None

    def all(self) -> List[Dict[str, Any]]:
        return self.products 