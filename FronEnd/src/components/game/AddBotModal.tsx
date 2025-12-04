import React, { useState } from 'react';
import { X } from 'lucide-react';
import { iaService } from '../../services/IAService';
import styles from './AddBotModal.module.css';
import { type AddBotModalProps } from '../../types/AI';


const DIFFICULTY_LEVELS = [
  { value: 'easy', label: 'Fácil' },
  { value: 'medium', label: 'Medio' },
  { value: 'hard', label: 'Difícil' },
  { value: 'expert', label: 'Experto' },
];

export const AddBotModal: React.FC<AddBotModalProps> = ({
  gameId,
  isOpen,
  onClose,
  onBotAdded,
}) => {
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('medium');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAddBot = async () => {
    setLoading(true);
    setError(null);
    try {
      await iaService.addBot(gameId, selectedDifficulty);
      onBotAdded();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al agregar bot');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>Agregar Bot</h2>
          <button
            onClick={onClose}
            className={styles.closeButton}
            aria-label="Cerrar modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className={styles.modalBody}>
          <p className={styles.description}>
            Selecciona el nivel de dificultad del bot:
          </p>

          <div className={styles.difficultiesGrid}>
            {DIFFICULTY_LEVELS.map((level) => (
              <button
                key={level.value}
                className={`${styles.difficultyBtn} ${
                  selectedDifficulty === level.value ? styles.selected : ''
                }`}
                onClick={() => setSelectedDifficulty(level.value)}
              >
                {level.label}
              </button>
            ))}
          </div>

          {error && <div className={styles.error}>{error}</div>}
        </div>

        <div className={styles.modalFooter}>
          <button onClick={onClose} className={styles.cancelBtn}>
            Cancelar
          </button>
          <button
            onClick={handleAddBot}
            className={styles.addBtn}
            disabled={loading}
          >
            {loading ? 'Agregando...' : 'Agregar Bot'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AddBotModal;
