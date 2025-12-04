import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Lock, Globe } from 'lucide-react';
import { gameService } from '../../services/gameService';
import styles from './CreateGame.module.css';

export const CreateGame: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    name: '',
    maxPlayers: 4,
    isPrivate: false,
    password: '',
    creatorColor: 'red',
  });

  const colors = ['red', 'blue', 'green', 'yellow'];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      setFormData(prev => ({
        ...prev,
        [name]: (e.target as HTMLInputElement).checked,
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value,
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim()) {
      setError('El nombre del juego es requerido');
      return;
    }

    if (formData.isPrivate && !formData.password.trim()) {
      setError('La contraseña es requerida para juegos privados');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const createRequest = {
        name: formData.name,
        max_players: parseInt(formData.maxPlayers.toString()),
        is_private: formData.isPrivate,
        password: formData.isPrivate ? formData.password : undefined,
        creator_color: formData.creatorColor,
      };

      const newGame = await gameService.createGame(createRequest);
      navigate(`/game/${newGame.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al crear el juego');
      console.error('Error creating game:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.headerInner}>
            <button
              onClick={() => navigate('/games')}
              className={styles.backButton}
            >
              <ArrowLeft className="w-5 h-5 text-text-primary" />
            </button>
            <h1 className={styles.headerTitle}>Crear Nueva Partida</h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className={styles.main}>
        <div className={styles.card}>
          <h2 className={styles.cardTitle}>
            Configura tu partida
          </h2>

          {error && (
            <div className={styles.errorAlert}>
              <p>{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className={styles.form}>
            {/* Nombre del Juego */}
            <div className={styles.formGroup}>
              <label htmlFor="name" className={styles.label}>
                Nombre de la Partida
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Ej: Partida Épica, Torneo 2024, etc."
                maxLength={100}
                className={styles.input}
              />
              <p className={styles.helpText}>
                {formData.name.length}/100 caracteres
              </p>
            </div>

            {/* Número de Jugadores */}
            <div className={styles.formGroup}>
              <label htmlFor="maxPlayers" className={styles.label}>
                Número de Jugadores
              </label>
              <select
                id="maxPlayers"
                name="maxPlayers"
                value={formData.maxPlayers}
                onChange={handleChange}
                className={styles.select}
              >
                <option value={2}>2 Jugadores</option>
                <option value={3}>3 Jugadores</option>
                <option value={4}>4 Jugadores</option>
              </select>
              <p className={styles.helpText}>
                Selecciona cuántos jugadores participarán
              </p>
            </div>

            {/* Color del Creador */}
            <div className={styles.formGroup}>
              <label htmlFor="creatorColor" className={styles.label}>
                Tu Color
              </label>
              <div className={styles.colorGrid}>
                {colors.map((color) => (
                  <button
                    key={color}
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, creatorColor: color }))}
                    className={`${styles.colorButton} ${formData.creatorColor === color ? styles.selected : ''}`}
                  >
                    {color === 'red' ? '🔴' : color === 'blue' ? '🔵' : color === 'green' ? '🟢' : '🟡'}
                  </button>
                ))}
              </div>
            </div>

            {/* Privacidad */}
            <div className={styles.formGroup}>
              <label className={styles.label}>
                Tipo de Partida
              </label>
              <div className={styles.privacyGroup}>
                <label className={styles.privacyOption}
                  onClick={() => setFormData(prev => ({ ...prev, isPrivate: false }))}>
                  <input
                    type="radio"
                    name="privacy"
                    checked={!formData.isPrivate}
                    onChange={() => setFormData(prev => ({ ...prev, isPrivate: false }))}
                    className={styles.privacyRadio}
                  />
                  <Globe className={`${styles.privacyIcon} text-success`} />
                  <div>
                    <p className={styles.privacyLabel}>Pública</p>
                    <p className={styles.privacyDescription}>Cualquiera puede unirse</p>
                  </div>
                </label>

                <label className={styles.privacyOption}
                  onClick={() => setFormData(prev => ({ ...prev, isPrivate: true }))}>
                  <input
                    type="radio"
                    name="privacy"
                    checked={formData.isPrivate}
                    onChange={() => setFormData(prev => ({ ...prev, isPrivate: true }))}
                    className={styles.privacyRadio}
                  />
                  <Lock className={`${styles.privacyIcon} text-warning`} />
                  <div>
                    <p className={styles.privacyLabel}>Privada</p>
                    <p className={styles.privacyDescription}>Requiere contraseña</p>
                  </div>
                </label>
              </div>
            </div>

            {/* Contraseña (si es privada) */}
            {formData.isPrivate && (
              <div className={styles.formGroup}>
                <label htmlFor="password" className={styles.label}>
                  Contraseña
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Ingresa una contraseña"
                  maxLength={50}
                  className={styles.input}
                />
                <p className={styles.helpText}>
                  Compartida con los jugadores que desees invitar
                </p>
              </div>
            )}

            {/* Resumen */}
            <div className={styles.summary}>
              <h3 className={styles.summaryTitle}>Resumen</h3>
              <div className={styles.summaryList}>
                <div className={styles.summaryItem}>
                  <span className={styles.summaryLabel}>Nombre:</span>
                  <span className={styles.summaryValue}>{formData.name || '—'}</span>
                </div>
                <div className={styles.summaryItem}>
                  <span className={styles.summaryLabel}>Jugadores:</span>
                  <span className={styles.summaryValue}>{formData.maxPlayers}</span>
                </div>
                <div className={styles.summaryItem}>
                  <span className={styles.summaryLabel}>Tipo:</span>
                  <span className={styles.summaryValue}>
                    {formData.isPrivate ? '🔒 Privada' : '🌐 Pública'}
                  </span>
                </div>
                <div className={styles.summaryItem}>
                  <span className={styles.summaryLabel}>Tu color:</span>
                  <span className={styles.summaryValue}>{formData.creatorColor}</span>
                </div>
              </div>
            </div>

            {/* Botones de Acción */}
            <div className={styles.actions}>
              <button
                type="button"
                onClick={() => navigate('/games')}
                className={`${styles.actionButton} ${styles.cancelButton}`}
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className={`${styles.actionButton} ${styles.submitButton}`}
              >
                {loading ? 'Creando...' : 'Crear Partida'}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
};
