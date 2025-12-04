export interface Recommendation {
  type: string;
  title: string;
  description: string;
  confidence: number;
  priority: number;
  data: Record<string, any>;
}

export interface RecommendationSet {
  user_id: string;
  recommendations: Recommendation[];
  generated_at: string;
  total_recommendations: number;
}