import type { DemoScene, Health, InferenceResult } from '../types'

async function getJson<T>(url: string): Promise<T> {
  const response = await fetch(url, { headers: { Accept: 'application/json' } })
  if (!response.ok) throw new Error(await friendlyError(response))
  return response.json() as Promise<T>
}

async function friendlyError(response: Response): Promise<string> {
  try {
    const data = await response.json()
    if (data?.detail) return Array.isArray(data.detail) ? data.detail[0]?.msg ?? 'Request failed' : String(data.detail)
  } catch {
    /* fall through */
  }
  return `Request failed (${response.status}). Check that the backend is running.`
}

export async function fetchHealth(): Promise<Health> {
  return getJson<Health>('/api/health')
}

export async function fetchScenes(): Promise<DemoScene[]> {
  const data = await getJson<{ scenes: DemoScene[] }>('/api/demo-scenes')
  return data.scenes
}

export async function runInference(input: { file?: File; sceneId?: string }): Promise<InferenceResult> {
  const body = new FormData()
  if (input.file) body.append('file', input.file)
  if (input.sceneId) body.append('demo_scene_id', input.sceneId)
  body.append('source_type', input.file ? 'upload' : 'demo')

  const response = await fetch('/api/infer', { method: 'POST', body })
  if (!response.ok) throw new Error(await friendlyError(response))
  return response.json() as Promise<InferenceResult>
}
