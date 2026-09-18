export interface SoilState {
  organic_carbon_pct?: number | null;
  ph?: number | null;
  moisture_pct?: number | null;
  nitrogen_ppm?: number | null;
  phosphorus_ppm?: number | null;
  potassium_ppm?: number | null;
  texture?: string | null;
}

export interface LandState {
  region?: string | null;
  land_use?: string | null;
  land_cover?: string | null;
  crop?: string | null;
  is_monoculture?: boolean | null;
  tree_cover_pct?: number | null;
  habitat_fragmentation?: string | null;
}

export interface BiodiversityState {
  species_richness?: string | number | null;
  habitat_diversity?: string | null;
  pollinator_presence?: string | null;
  native_species_ratio?: number | null;
  biodiversity_indicators?: string[];
}

export interface ClimateState {
  rainfall?: string | null;
  rainfall_variability?: string | null;
  annual_rainfall_mm?: number | null;
  temperature_celsius?: number | null;
  drought_frequency?: string | null;
  water_availability?: string | null;
}

export interface HumanImpactState {
  pesticide_use?: string | null;
  pollution_level?: string | null;
  water_extraction?: string | null;
  deforestation_proximity?: string | null;
  urbanization_pressure?: string | null;
}

export interface EnvironmentalState {
  soil: SoilState;
  land: LandState;
  biodiversity: BiodiversityState;
  climate: ClimateState;
  human_impact: HumanImpactState;
}

export interface RetrievedEvidence {
  source_title: string;
  organization: string;
  year: number;
  document_type: string;
  relevance_score: number;
  evidence_text: string;
  reported_change?: string | null;
  doi_or_url?: string | null;
  vector_distance?: number | null;
  semantic_similarity?: number | null;
  reranking_score?: number | null;
  match_rationale?: string | null;
}

export interface RetrievalTrace {
  query: string;
  retrieval_mode?: string;
  vector_backend?: string;
  vector_retrieved_ids?: string[];
  filters_applied?: Record<string, any>;
  sources: RetrievedEvidence[];
  total_documents_scanned?: number;
  top_score?: number;
}

export interface RecommendationOutput {
  id: string;
  title: string;
  directive: string;
  scientific_rationale: string;
  environmental_metrics_affected: string[];
  time_horizon: string;
  confidence: string;
  evidence: RetrievedEvidence[];
  why_this_recommendation: string[];
}

export interface ChatRequest {
  conversation_id?: string | null;
  land_profile_id?: string | null;
  message: string;
  structured_state?: Partial<EnvironmentalState> | null;
}

export interface ChatResponse {
  conversation_id: string;
  message: string;
  extracted_state: EnvironmentalState;
  is_information_complete: boolean;
  clarifying_questions: string[];
  recommendations: RecommendationOutput[];
  retrieval_trace?: RetrievalTrace | null;
  multi_metric_stressors: string[];
  detected_interactions: string[];
}

export interface LandProfileResponse {
  id: string;
  name: string;
  region: string;
  latitude?: number | null;
  longitude?: number | null;
  area_hectares: number;
  primary_crop: string;
  farming_system: string;
  created_at: string;
  updated_at: string;
  current_state: EnvironmentalState;
}

export interface DashboardData {
  land_id: string;
  name: string;
  region: string;
  primary_crop: string;
  farming_system: string;
  metrics: EnvironmentalState;
  active_stressors: string[];
  cross_variable_couplings: string[];
  recent_recommendations: RecommendationOutput[];
}

export interface CorpusDocument {
  id: string;
  title: string;
  organization: string;
  year: number;
  document_type: string;
  region?: string;
  metrics?: string[];
  target_metrics?: string[];
  agroecological_zones?: string[];
  doi_or_url?: string;
  quantified_claims_count: number;
}

export interface SystemHealth {
  status: string;
  service: string;
  tagline: string;
  environment: string;
  knowledge_corpus_documents: number;
  vector_index_active: boolean;
}
