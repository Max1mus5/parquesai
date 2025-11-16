"""
Niveles de dificultad para el bot IA
"""
from enum import Enum
from typing import Dict, Any

class DifficultyLevel(Enum):
    """Niveles de dificultad del bot IA"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class DifficultyConfig:
    """Configuración para cada nivel de dificultad"""
    
    CONFIGS: Dict[DifficultyLevel, Dict[str, Any]] = {
        DifficultyLevel.EASY: {
            "algorithm": "random",
            "depth": 1,
            "simulations": 100,
            "exploration_constant": 1.4,
            "thinking_time": 0.5,
            "mistake_probability": 0.3,
            "aggressive_play": 0.2,
            "defensive_play": 0.8,
            "description": "Juega de forma básica con movimientos aleatorios mejorados"
        },
        DifficultyLevel.MEDIUM: {
            "algorithm": "minimax",
            "depth": 2,
            "simulations": 500,
            "exploration_constant": 1.2,
            "thinking_time": 1.0,
            "mistake_probability": 0.15,
            "aggressive_play": 0.4,
            "defensive_play": 0.6,
            "description": "Usa Minimax con profundidad limitada y estrategia balanceada"
        },
        DifficultyLevel.HARD: {
            "algorithm": "minimax",
            "depth": 3,
            "simulations": 1000,
            "exploration_constant": 1.0,
            "thinking_time": 1.5,
            "mistake_probability": 0.05,
            "aggressive_play": 0.6,
            "defensive_play": 0.4,
            "description": "Minimax avanzado con mayor profundidad y juego agresivo"
        },
        DifficultyLevel.EXPERT: {
            "algorithm": "mcts",
            "depth": 4,
            "simulations": 2000,
            "exploration_constant": 0.8,
            "thinking_time": 2.0,
            "mistake_probability": 0.01,
            "aggressive_play": 0.7,
            "defensive_play": 0.3,
            "description": "MCTS con alta simulación y estrategia óptima"
        }
    }
    
    @classmethod
    def get_config(cls, difficulty: DifficultyLevel) -> Dict[str, Any]:
        """Obtener configuración para un nivel de dificultad"""
        return cls.CONFIGS.get(difficulty, cls.CONFIGS[DifficultyLevel.MEDIUM])
    
    @classmethod
    def get_all_levels(cls) -> Dict[str, Dict[str, Any]]:
        """Obtener todos los niveles de dificultad disponibles"""
        return {level.value: config for level, config in cls.CONFIGS.items()}