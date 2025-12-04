import React, { useState } from 'react';
import { Lightbulb, RefreshCw, ChevronDown, ChevronUp } from 'lucide-react';
import { recommendationsService } from '../../services/recommendationsService';
import styles from './RecommendationsPanel.module.css';

type RecommendationType = 'general' | 'strategy' | 'opponents' | 'training' | 'improvements' | 'challenges' | 'pattern' | 'stats';

export const RecommendationsPanel: React.FC = () => {
  const [activeTab, setActiveTab] = useState<RecommendationType>('general');
  const [expanded, setExpanded] = useState(false);
  const [recommendationsData, setRecommendationsData] = useState<Record<RecommendationType, any>>({
    general: null,
    strategy: null,
    opponents: null,
    training: null,
    improvements: null,
    challenges: null,
    pattern: null,
    stats: null,
  });
  const [loadingTabs, setLoadingTabs] = useState<Record<RecommendationType, boolean>>({
    general: false,
    strategy: false,
    opponents: false,
    training: false,
    improvements: false,
    challenges: false,
    pattern: false,
    stats: false,
  });
  const [errorTabs, setErrorTabs] = useState<Record<RecommendationType, string | null>>({
    general: null,
    strategy: null,
    opponents: null,
    training: null,
    improvements: null,
    challenges: null,
    pattern: null,
    stats: null,
  });

  const loadRecommendations = async (type: RecommendationType) => {
    setLoadingTabs(prev => ({ ...prev, [type]: true }));
    setErrorTabs(prev => ({ ...prev, [type]: null }));

    try {
      let data;
      switch (type) {
        case 'general':
          data = await recommendationsService.getUserRecommendations(true);
          break;
        case 'strategy':
          data = await recommendationsService.getStrategyRecommendations();
          break;
        case 'opponents':
          data = await recommendationsService.getOpponentRecommendations();
          break;
        case 'training':
          data = await recommendationsService.getTrainingRecommendations();
          break;
        case 'improvements':
          data = await recommendationsService.getImprovementSuggestions();
          break;
        case 'challenges':
          data = await recommendationsService.getChallenges();
          break;
        case 'pattern':
          data = await recommendationsService.getPlayerPattern();
          break;
        case 'stats':
          data = await recommendationsService.getStats();
          break;
        default:
          throw new Error('Tipo de recomendación desconocido');
      }
      setRecommendationsData(prev => ({ ...prev, [type]: data }));
    } catch (err) {
      setErrorTabs(prev => ({
        ...prev,
        [type]: err instanceof Error ? err.message : 'Error al cargar recomendaciones',
      }));
    } finally {
      setLoadingTabs(prev => ({ ...prev, [type]: false }));
    }
  };

  const handleTabClick = (type: RecommendationType) => {
    setActiveTab(type);
  };

  const getPriorityColor = (priority: number): string => {
    if (priority === 1) return '#ef4444';
    if (priority === 2) return '#eab308';
    return '#16a34a';
  };

  const getConfidencePercentage = (confidence: number): number => {
    return Math.round(confidence * 100);
  };

  const renderTabContent = () => {
    const data = recommendationsData[activeTab];
    const error = errorTabs[activeTab];
    const loading = loadingTabs[activeTab];

    if (loading) {
      return <div className={styles.loadingState}>Cargando...</div>;
    }

    if (error) {
      return (
        <div className={styles.errorBox}>
          <p className={styles.errorText}>{error}</p>
        </div>
      );
    }

    if (!data) {
      return (
        <div className={styles.emptyState}>
          <p className={styles.emptyText}>Haz click en "Pedir Recomendación" para cargar datos</p>
          <button
            onClick={() => loadRecommendations(activeTab)}
            className={styles.loadButton}
          >
            <RefreshCw className={styles.refreshIcon} />
            <span>Pedir Recomendación</span>
          </button>
        </div>
      );
    }

    // Renderizar según el tipo
    if (activeTab === 'general' && data.recommendations) {
      return renderRecommendationsList(data);
    }

    if (activeTab === 'strategy' && Array.isArray(data)) {
      return renderRecommendationsList({ recommendations: data });
    }

    if (activeTab === 'opponents' && Array.isArray(data)) {
      return renderRecommendationsList({ recommendations: data });
    }

    if (activeTab === 'training' && Array.isArray(data)) {
      return renderRecommendationsList({ recommendations: data });
    }

    if (activeTab === 'improvements') {
      return renderImprovementSuggestions(data);
    }

    if (activeTab === 'challenges' && Array.isArray(data)) {
      return renderChallenges(data);
    }

    if (activeTab === 'pattern') {
      return renderPlayerPattern(data);
    }

    if (activeTab === 'stats') {
      return renderStats(data);
    }

    return (
      <pre className={styles.jsonPreview}>
        {JSON.stringify(data, null, 2)}
      </pre>
    );
  };

  const renderRecommendationsList = (data: any) => {
    const recs = data.recommendations || data;
    return (
      <div className={styles.recommendationsList}>
        {Array.isArray(recs) && recs.length > 0 ? (
          recs.map((rec: any, index: number) => (
            <div key={index} className={styles.recommendationCard}>
              <div className={styles.cardHeader}>
                <div className={styles.titleSection}>
                  <h4 className={styles.title}>{rec.title}</h4>
                  <div className={styles.badges}>
                    <span
                      className={styles.priorityBadge}
                      style={{ backgroundColor: getPriorityColor(rec.priority) }}
                    >
                      {rec.priority === 1
                        ? 'Alta'
                        : rec.priority === 2
                        ? 'Media'
                        : 'Baja'}
                    </span>
                    <span className={styles.typeBadge}>{rec.type}</span>
                  </div>
                </div>
                <div className={styles.confidence}>
                  <div className={styles.confidenceBar}>
                    <div
                      className={styles.confidenceFill}
                      style={{
                        width: `${getConfidencePercentage(rec.confidence)}%`,
                        backgroundColor:
                          rec.confidence > 0.7
                            ? '#16a34a'
                            : rec.confidence > 0.5
                            ? '#eab308'
                            : '#ef4444',
                      }}
                    />
                  </div>
                  <span className={styles.confidenceText}>
                    {getConfidencePercentage(rec.confidence)}%
                  </span>
                </div>
              </div>

              <p className={styles.description}>{rec.description}</p>

              {rec.data && Object.keys(rec.data).length > 0 && (
                <div className={styles.dataSection}>
                  <details className={styles.details}>
                    <summary className={styles.summary}>Detalles</summary>
                    <pre className={styles.dataContent}>
                      {JSON.stringify(rec.data, null, 2)}
                    </pre>
                  </details>
                </div>
              )}
            </div>
          ))
        ) : (
          <p className={styles.noRecommendations}>
            No hay recomendaciones disponibles
          </p>
        )}
      </div>
    );
  };

  const renderImprovementSuggestions = (data: any) => (
    <div className={styles.improvementContainer}>
      <div className={styles.improvementSection}>
        <h4 className={styles.sectionTitle}>Nivel de Habilidad</h4>
        <p className={styles.improvementLevel}>{data.overall_skill_level}</p>
      </div>

      {data.strengths && data.strengths.length > 0 && (
        <div className={styles.improvementSection}>
          <h4 className={styles.sectionTitle}>Fortalezas</h4>
          <ul className={styles.improvementList}>
            {data.strengths.map((strength: string, idx: number) => (
              <li key={idx}>{strength}</li>
            ))}
          </ul>
        </div>
      )}

      {data.improvement_areas && data.improvement_areas.length > 0 && (
        <div className={styles.improvementSection}>
          <h4 className={styles.sectionTitle}>Áreas de Mejora</h4>
          <div className={styles.improvementAreas}>
            {data.improvement_areas.map((area: any, idx: number) => (
              <div key={idx} className={styles.improvementArea}>
                <h5 className={styles.areaName}>{area.name}</h5>
                <p className={styles.areaDescription}>{area.description}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {data.next_steps && data.next_steps.length > 0 && (
        <div className={styles.improvementSection}>
          <h4 className={styles.sectionTitle}>Próximos Pasos</h4>
          <ol className={styles.improvementList}>
            {data.next_steps.map((step: string, idx: number) => (
              <li key={idx}>{step}</li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );

  const renderChallenges = (challenges: any[]) => (
    <div className={styles.challengesList}>
      {challenges.length > 0 ? (
        challenges.map((challenge, idx) => (
          <div key={idx} className={styles.challengeCard}>
            <div className={styles.challengeHeader}>
              <h4 className={styles.challengeTitle}>{challenge.title}</h4>
              <span className={styles.difficultyBadge}>{challenge.difficulty}</span>
            </div>
            <p className={styles.challengeDescription}>{challenge.description}</p>
            <div className={styles.challengeProgress}>
              <div className={styles.progressBar}>
                <div
                  className={styles.progressFill}
                  style={{
                    width: `${(challenge.current / challenge.target) * 100}%`,
                  }}
                />
              </div>
              <span className={styles.progressText}>
                {challenge.current} / {challenge.target}
              </span>
            </div>
            {challenge.reward && (
              <p className={styles.challengeReward}>🏆 Recompensa: {challenge.reward}</p>
            )}
          </div>
        ))
      ) : (
        <p className={styles.noRecommendations}>No hay desafíos disponibles</p>
      )}
    </div>
  );

  const renderPlayerPattern = (pattern: any) => (
    <div className={styles.patternContainer}>
      <div className={styles.patternSection}>
        <h4 className={styles.sectionTitle}>Estilo de Juego</h4>
        <p className={styles.patternValue}>{pattern.play_style}</p>
      </div>

      {pattern.preferred_colors && (
        <div className={styles.patternSection}>
          <h4 className={styles.sectionTitle}>Colores Preferidos</h4>
          <div className={styles.colorsList}>
            {pattern.preferred_colors.map((color: string, idx: number) => (
              <span key={idx} className={styles.colorTag}>
                {color}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className={styles.patternStats}>
        <div className={styles.statBox}>
          <span className={styles.statLabel}>Tasa de Victoria</span>
          <span className={styles.statValue}>
            {(pattern.win_rate * 100).toFixed(1)}%
          </span>
        </div>
        <div className={styles.statBox}>
          <span className={styles.statLabel}>Duración Promedio</span>
          <span className={styles.statValue}>{pattern.avg_game_duration.toFixed(1)}m</span>
        </div>
        <div className={styles.statBox}>
          <span className={styles.statLabel}>Tolerancia al Riesgo</span>
          <span className={styles.statValue}>
            {(pattern.risk_tolerance * 100).toFixed(0)}%
          </span>
        </div>
        <div className={styles.statBox}>
          <span className={styles.statLabel}>Adaptabilidad</span>
          <span className={styles.statValue}>
            {(pattern.adaptability * 100).toFixed(0)}%
          </span>
        </div>
        <div className={styles.statBox}>
          <span className={styles.statLabel}>Consistencia</span>
          <span className={styles.statValue}>
            {(pattern.consistency * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {pattern.favorite_strategies && (
        <div className={styles.patternSection}>
          <h4 className={styles.sectionTitle}>Estrategias Favoritas</h4>
          <ul className={styles.strategiesList}>
            {pattern.favorite_strategies.map((strategy: string, idx: number) => (
              <li key={idx}>{strategy}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );

  const renderStats = (stats: any) => (
    <div className={styles.statsContainer}>
      <div className={styles.statBox}>
        <span className={styles.statLabel}>Total de Recomendaciones</span>
        <span className={styles.statValue}>{stats.total_recommendations}</span>
      </div>

      {stats.by_type && (
        <div className={styles.patternSection}>
          <h4 className={styles.sectionTitle}>Por Tipo</h4>
          <ul className={styles.statsList}>
            {Object.entries(stats.by_type).map(([type, count]: [string, unknown]) => (
              <li key={type}>
                {type}: <strong>{String(count)}</strong>
              </li>
            ))}
          </ul>
        </div>
      )}

      {stats.by_priority && (
        <div className={styles.patternSection}>
          <h4 className={styles.sectionTitle}>Por Prioridad</h4>
          <ul className={styles.statsList}>
            {Object.entries(stats.by_priority).map(([priority, count]: [string, unknown]) => (
              <li key={priority}>
                {priority}: <strong>{String(count)}</strong>
              </li>
            ))}
          </ul>
        </div>
      )}

      {stats.average_confidence && (
        <div className={styles.statBox}>
          <span className={styles.statLabel}>Confianza Promedio</span>
          <span className={styles.statValue}>
            {(stats.average_confidence * 100).toFixed(1)}%
          </span>
        </div>
      )}
    </div>
  );

  const tabs: { type: RecommendationType; label: string }[] = [
    { type: 'general', label: 'General' },
    { type: 'strategy', label: 'Estrategia' },
    { type: 'opponents', label: 'Oponentes' },
    { type: 'training', label: 'Entrenamiento' },
    { type: 'improvements', label: 'Mejoras' },
    { type: 'challenges', label: 'Desafíos' },
    { type: 'pattern', label: 'Patrón' },
    { type: 'stats', label: 'Estadísticas' },
  ];

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <button
          onClick={() => setExpanded(!expanded)}
          className={styles.toggleButton}
        >
          <Lightbulb className={styles.headerIcon} />
          <span className={styles.headerTitle}>Recomendaciones</span>
          {expanded ? (
            <ChevronUp className={styles.chevron} />
          ) : (
            <ChevronDown className={styles.chevron} />
          )}
        </button>
      </div>

      {expanded && (
        <div className={styles.content}>
          <div className={styles.tabsContainer}>
            {tabs.map(tab => (
              <button
                key={tab.type}
                onClick={() => handleTabClick(tab.type)}
                className={`${styles.tab} ${activeTab === tab.type ? styles.tabActive : ''}`}
              >
                {tab.label}
                {loadingTabs[tab.type] && <span className={styles.tabLoader}>...</span>}
              </button>
            ))}
          </div>

          <div className={styles.tabContent}>
            {renderTabContent()}
          </div>
        </div>
      )}
    </div>
  );
};
