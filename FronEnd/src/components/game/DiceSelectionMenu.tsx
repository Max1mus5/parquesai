import React from 'react';
import styles from './DiceSelectionMenu.module.css';

interface DiceSelectionMenuProps {
  dice1: number;
  dice2: number;
  total: number;
  isPair: boolean;
  onSelectDice1: () => void;
  onSelectDice2: () => void;
  onSelectTotal: () => void;
  onClose: () => void;
}

export const DiceSelectionMenu: React.FC<DiceSelectionMenuProps> = ({
  dice1,
  dice2,
  total,
  isPair,
  onSelectDice1,
  onSelectDice2,
  onSelectTotal,
  onClose,
}) => {
  return (
    <div className={styles.overlay}>
      <div className={styles.menu}>
        <div className={styles.header}>
          <h3>¿Con qué dado mover esta ficha?</h3>
          {isPair && <span className={styles.pairBadge}>PAR ✓</span>}
        </div>
        
        <div className={styles.diceDisplay}>
          <div className={styles.diceBox}>
            <span className={styles.diceValue}>{dice1}</span>
          </div>
          <span className={styles.plus}>+</span>
          <div className={styles.diceBox}>
            <span className={styles.diceValue}>{dice2}</span>
          </div>
          <span className={styles.equals}>=</span>
          <div className={styles.diceBox}>
            <span className={styles.diceValue}>{total}</span>
          </div>
        </div>

        <div className={styles.options}>
          {dice1 > 0 && (
            <button 
              className={styles.optionButton}
              onClick={onSelectDice1}
            >
              <div className={styles.optionContent}>
                <span className={styles.optionValue}>{dice1}</span>
                <span className={styles.optionLabel}>Mover con Dado 1</span>
              </div>
            </button>
          )}

          {dice2 > 0 && (
            <button 
              className={styles.optionButton}
              onClick={onSelectDice2}
            >
              <div className={styles.optionContent}>
                <span className={styles.optionValue}>{dice2}</span>
                <span className={styles.optionLabel}>Mover con Dado 2</span>
              </div>
            </button>
          )}

          {total > 0 && (
            <button 
              className={`${styles.optionButton} ${styles.totalOption}`}
              onClick={onSelectTotal}
            >
              <div className={styles.optionContent}>
                <span className={styles.optionValue}>{total}</span>
                <span className={styles.optionLabel}>Mover con Total (Suma)</span>
              </div>
            </button>
          )}
        </div>

        <button className={styles.closeButton} onClick={onClose}>
          Cancelar
        </button>
      </div>
    </div>
  );
};
