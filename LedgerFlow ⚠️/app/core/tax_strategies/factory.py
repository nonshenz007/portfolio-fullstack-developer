"""
Tax Strategy Factory

This module provides a factory for creating tax strategy instances and
supports plugin discovery through entry points.

Key features:
- Strategy creation by name or country
- Plugin discovery through entry points
- Automatic strategy registration
- Fallback to built-in strategies
"""

import importlib.metadata
from typing import Dict, Type, Optional, List
from .base import TaxStrategy, TaxContext
from .gst_strategy import GSTStrategy
from .vat_strategy import VATStrategy
from .no_tax_strategy import NoTaxStrategy


class TaxStrategyFactory:
    """
    Factory for creating tax strategy instances
    
    This factory supports both built-in strategies and plugin strategies
    discovered through entry points.
    """
    
    # Built-in strategies
    _builtin_strategies: Dict[str, Type[TaxStrategy]] = {
        'gst': GSTStrategy,
        'vat': VATStrategy,
        'no_tax': NoTaxStrategy,
        'cash': NoTaxStrategy,  # Alias for no_tax
    }
    
    # Plugin strategies discovered through entry points
    _plugin_strategies: Dict[str, Type[TaxStrategy]] = {}
    
    # Country to strategy mapping
    _country_mapping: Dict[str, str] = {
        'India': 'gst',
        'IN': 'gst',
        'Bahrain': 'vat',
        'BH': 'vat',
    }
    
    @classmethod
    def create_strategy(cls, strategy_name: str, **kwargs) -> TaxStrategy:
        """
        Create a tax strategy instance by name
        
        Args:
            strategy_name: Name of the strategy ('gst', 'vat', 'no_tax', etc.)
            **kwargs: Additional arguments to pass to strategy constructor
            
        Returns:
            TaxStrategy instance
            
        Raises:
            ValueError: If strategy is not found
        """
        strategy_name = strategy_name.lower()
        
        # Try plugin strategies first
        if strategy_name in cls._plugin_strategies:
            strategy_class = cls._plugin_strategies[strategy_name]
            return strategy_class(**kwargs)
        
        # Try built-in strategies
        if strategy_name in cls._builtin_strategies:
            strategy_class = cls._builtin_strategies[strategy_name]
            return strategy_class(**kwargs)
        
        # Strategy not found
        available = list(cls._builtin_strategies.keys()) + list(cls._plugin_strategies.keys())
        raise ValueError(f"Unknown tax strategy '{strategy_name}'. Available strategies: {available}")
    
    @classmethod
    def create_strategy_for_country(cls, country: str, **kwargs) -> TaxStrategy:
        """
        Create a tax strategy instance for a specific country
        
        Args:
            country: Country name or code
            **kwargs: Additional arguments to pass to strategy constructor
            
        Returns:
            TaxStrategy instance
            
        Raises:
            ValueError: If no strategy is found for the country
        """
        strategy_name = cls._country_mapping.get(country)
        if not strategy_name:
            raise ValueError(f"No tax strategy found for country '{country}'")
        
        return cls.create_strategy(strategy_name, **kwargs)
    
    @classmethod
    def create_strategy_for_context(cls, context: TaxContext, **kwargs) -> TaxStrategy:
        """
        Create a tax strategy instance based on context
        
        Args:
            context: Tax calculation context
            **kwargs: Additional arguments to pass to strategy constructor
            
        Returns:
            TaxStrategy instance
        """
        # Try to determine strategy from business country
        try:
            return cls.create_strategy_for_country(context.business_country, **kwargs)
        except ValueError:
            pass
        
        # Try to determine strategy from customer country
        try:
            return cls.create_strategy_for_country(context.customer_country, **kwargs)
        except ValueError:
            pass
        
        # Fallback to currency-based detection
        if context.currency == 'INR':
            return cls.create_strategy('gst', **kwargs)
        elif context.currency == 'BHD':
            return cls.create_strategy('vat', **kwargs)
        
        # Final fallback to no-tax strategy
        return cls.create_strategy('no_tax', **kwargs)
    
    @classmethod
    def register_strategy(cls, name: str, strategy_class: Type[TaxStrategy]) -> None:
        """
        Register a new tax strategy
        
        Args:
            name: Strategy name
            strategy_class: Strategy class
        """
        if not issubclass(strategy_class, TaxStrategy):
            raise ValueError(f"Strategy class must inherit from TaxStrategy")
        
        cls._plugin_strategies[name.lower()] = strategy_class
    
    @classmethod
    def register_country_mapping(cls, country: str, strategy_name: str) -> None:
        """
        Register a country to strategy mapping
        
        Args:
            country: Country name or code
            strategy_name: Strategy name
        """
        cls._country_mapping[country] = strategy_name.lower()
    
    @classmethod
    def discover_plugins(cls) -> None:
        """
        Discover and register plugin strategies through entry points
        
        This method looks for entry points in the 'ledgerflow.tax_strategies'
        group and registers them automatically.
        """
        try:
            # Discover entry points
            entry_points = importlib.metadata.entry_points()
            
            # Look for tax strategy plugins
            if hasattr(entry_points, 'select'):
                # Python 3.10+ style
                tax_strategies = entry_points.select(group='ledgerflow.tax_strategies')
            else:
                # Python 3.9 style
                tax_strategies = entry_points.get('ledgerflow.tax_strategies', [])
            
            for entry_point in tax_strategies:
                try:
                    strategy_class = entry_point.load()
                    cls.register_strategy(entry_point.name, strategy_class)
                    print(f"Registered tax strategy plugin: {entry_point.name}")
                except Exception as e:
                    print(f"Failed to load tax strategy plugin '{entry_point.name}': {e}")
                    
        except Exception as e:
            print(f"Failed to discover tax strategy plugins: {e}")
    
    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """
        Get list of all available strategy names
        
        Returns:
            List of strategy names
        """
        return list(cls._builtin_strategies.keys()) + list(cls._plugin_strategies.keys())
    
    @classmethod
    def get_supported_countries(cls) -> List[str]:
        """
        Get list of all supported countries
        
        Returns:
            List of country names/codes
        """
        return list(cls._country_mapping.keys())
    
    @classmethod
    def get_strategy_info(cls, strategy_name: str) -> Dict[str, any]:
        """
        Get information about a specific strategy
        
        Args:
            strategy_name: Name of the strategy
            
        Returns:
            Dictionary with strategy information
        """
        strategy_name = strategy_name.lower()
        
        # Find strategy class
        strategy_class = None
        is_plugin = False
        
        if strategy_name in cls._plugin_strategies:
            strategy_class = cls._plugin_strategies[strategy_name]
            is_plugin = True
        elif strategy_name in cls._builtin_strategies:
            strategy_class = cls._builtin_strategies[strategy_name]
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        # Create temporary instance to get info
        try:
            instance = strategy_class()
            return {
                'name': strategy_name,
                'class_name': strategy_class.__name__,
                'is_plugin': is_plugin,
                'supported_countries': instance.get_supported_countries(),
                'supported_currencies': instance.get_supported_currencies(),
                'description': strategy_class.__doc__ or 'No description available'
            }
        except Exception as e:
            return {
                'name': strategy_name,
                'class_name': strategy_class.__name__,
                'is_plugin': is_plugin,
                'error': f"Failed to get strategy info: {e}"
            }


# Auto-discover plugins on module import
TaxStrategyFactory.discover_plugins()