export type Mode = 'development' | 'model'

export interface Health {
  status: string
  mode: Mode
  model_version: string
  is_ai_inference: boolean
  checkpoint_available: boolean
  torch_available: boolean
  runner_note: string
  demo_scene_count: number
  disclaimer: string
  timestamp: string
}

export interface DemoScene {
  id: string
  name: string
  scene_type: string
  region_label: string
  description: string
  image_url: string
  data_note: string
}

export interface ConfidenceSummary {
  mean: number
  low_pct: number
  medium_pct: number
  high_pct: number
  level: 'low' | 'medium' | 'high'
  method_note: string
}

export interface InferenceResult {
  result_id: string
  created_at: string
  mode: Mode
  model_version: string
  is_ai_inference: boolean
  source: { type: 'demo' | 'upload'; name: string; filename: string; scene_id: string | null }
  input: { width: number; height: number; channels: number; preprocessing: string; input_kind?: string; polarizations?: string[]; crs?: string | null; transform?: number[] | null }
  feature_estimates: Record<string, number>
  feature_method: string
  confidence_summary: ConfidenceSummary
  confidence_method: string
  metrics: {
    runtime_ms: number
    input_output_edge_agreement_proxy: number
    edge_method: string
    held_out_evaluation: string
  }
  disclaimer: string
  privacy: string
  urls: { input: string; colour: string; confidence: string; json: string; geotiff?: string | null }
}
