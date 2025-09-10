"""
Configuration API endpoints for LedgerFlow

Provides REST API endpoints for:
- Loading configuration
- Validating configuration
- Hot-reloading configuration
- Getting configuration schema
"""

from flask import Blueprint, request, jsonify, current_app
from typing import Dict, Any
import logging

from app.core.config_manager import get_config_manager, ValidationResult

logger = logging.getLogger(__name__)

config_bp = Blueprint('config', __name__, url_prefix='/api/config')


@config_bp.route('/schema/<config_name>', methods=['GET'])
def get_config_schema(config_name: str):
    """
    Get JSON schema for a configuration
    
    Args:
        config_name: Name of the configuration schema to retrieve
        
    Returns:
        JSON schema or 404 if not found
    """
    try:
        config_manager = get_config_manager()
        
        if config_name in config_manager._schemas:
            return jsonify({
                'schema': config_manager._schemas[config_name],
                'config_name': config_name
            })
        else:
            return jsonify({
                'error': f'Schema not found for configuration: {config_name}'
            }), 404
            
    except Exception as e:
        logger.error(f"Error retrieving schema for {config_name}: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@config_bp.route('/<config_name>', methods=['GET'])
def get_config(config_name: str):
    """
    Get configuration by name
    
    Args:
        config_name: Name of the configuration to retrieve
        
    Returns:
        Configuration data or error
    """
    try:
        config_manager = get_config_manager()
        config_data = config_manager.load_config(config_name)
        
        return jsonify({
            'config': config_data,
            'config_name': config_name
        })
        
    except Exception as e:
        logger.error(f"Error loading configuration {config_name}: {e}")
        return jsonify({
            'error': 'Configuration not found or invalid',
            'message': str(e)
        }), 404


@config_bp.route('/<config_name>/validate', methods=['POST'])
def validate_config(config_name: str):
    """
    Validate configuration data against schema
    
    Args:
        config_name: Name of the configuration schema to validate against
        
    Returns:
        Validation result with HTTP 400 for validation errors
    """
    try:
        if not request.is_json:
            return jsonify({
                'error': 'Request must be JSON',
                'valid': False
            }), 400
        
        config_data = request.get_json()
        if not config_data:
            return jsonify({
                'error': 'Empty configuration data',
                'valid': False
            }), 400
        
        config_manager = get_config_manager()
        validation_result = config_manager.validate_config(config_data, config_name)
        
        response_data = {
            'valid': validation_result.valid,
            'config_name': config_name
        }
        
        if validation_result.errors:
            response_data['errors'] = validation_result.errors
        
        if validation_result.warnings:
            response_data['warnings'] = validation_result.warnings
        
        # Return HTTP 400 for validation errors as per FR-3 requirement
        if not validation_result.valid:
            return jsonify(response_data), 400
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error validating configuration {config_name}: {e}")
        return jsonify({
            'error': 'Validation failed',
            'message': str(e),
            'valid': False
        }), 500


@config_bp.route('/<config_name>/reload', methods=['POST'])
def reload_config(config_name: str):
    """
    Hot-reload configuration
    
    Args:
        config_name: Name of the configuration to reload
        
    Returns:
        Reload result
    """
    try:
        config_manager = get_config_manager()
        success = config_manager.hot_reload_config(config_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Configuration {config_name} reloaded successfully',
                'config_name': config_name
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Failed to reload configuration {config_name}',
                'config_name': config_name
            }), 500
            
    except Exception as e:
        logger.error(f"Error reloading configuration {config_name}: {e}")
        return jsonify({
            'success': False,
            'error': 'Reload failed',
            'message': str(e)
        }), 500


@config_bp.route('/status', methods=['GET'])
def get_config_status():
    """
    Get status of configuration manager
    
    Returns:
        Configuration manager status
    """
    try:
        config_manager = get_config_manager()
        status = config_manager.get_config_status()
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting configuration status: {e}")
        return jsonify({
            'error': 'Failed to get status',
            'message': str(e)
        }), 500


@config_bp.route('/reload-all', methods=['POST'])
def reload_all_configs():
    """
    Reload all cached configurations
    
    Returns:
        Reload result for all configurations
    """
    try:
        config_manager = get_config_manager()
        config_manager.reload_all_configs()
        
        return jsonify({
            'success': True,
            'message': 'All configurations reloaded successfully'
        })
        
    except Exception as e:
        logger.error(f"Error reloading all configurations: {e}")
        return jsonify({
            'success': False,
            'error': 'Reload failed',
            'message': str(e)
        }), 500


@config_bp.route('/schema/simulation-config', methods=['GET'])
def get_simulation_config_schema():
    """
    Get simulation configuration schema for UI generation (FR-4 requirement)
    
    Returns:
        JSON schema for simulation configuration
    """
    try:
        config_manager = get_config_manager()
        
        if 'simulation' in config_manager._schemas:
            schema = config_manager._schemas['simulation']
            
            # Add UI-specific metadata
            ui_schema = {
                'schema': schema,
                'ui_hints': {
                    'realism_profile': {
                        'widget': 'select',
                        'description': 'Choose the realism level for invoice generation'
                    },
                    'simulation.default_invoice_count': {
                        'widget': 'number',
                        'min': 1,
                        'max': 10000
                    },
                    'timeflow.reality_buffer': {
                        'widget': 'slider',
                        'min': 0,
                        'max': 100,
                        'step': 5
                    },
                    'timeflow.believability_stress': {
                        'widget': 'slider',
                        'min': 0,
                        'max': 100,
                        'step': 5
                    }
                }
            }
            
            return jsonify(ui_schema)
        else:
            return jsonify({
                'error': 'Simulation configuration schema not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error retrieving simulation config schema: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


# Error handlers
@config_bp.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    return jsonify({
        'error': 'Bad request',
        'message': 'Invalid request data or validation failed'
    }), 400


@config_bp.errorhandler(404)
def not_found(error):
    """Handle not found errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'Configuration or schema not found'
    }), 404


@config_bp.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500