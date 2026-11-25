import { FileImage, Upload, X } from 'lucide-react'
import { useRef, useState } from 'react'

interface Props {
  file: File | null
  onFile: (file: File | null) => void
  onError: (message: string) => void
  disabled: boolean
  pngPrototype?: boolean
}

export function UploadDropzone({ file, onFile, onError, disabled, pngPrototype = false }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  function accept(candidate?: File) {
    if (!candidate) return
    const suffix = candidate.name.toLowerCase().split('.').pop()
    const okType = pngPrototype ? suffix === 'png' : ['png', 'jpg', 'jpeg', 'tif', 'tiff'].includes(suffix ?? '')
    if (!okType) {
      onFile(null)
      onError(pngPrototype
        ? 'This prototype checkpoint expects a grayscale PNG tile.'
        : 'Unsupported file type. Use a 2-band GeoTIFF (VV band 1, VH band 2), PNG or JPEG preview.')
      return
    }
    const maxBytes = ['tif', 'tiff'].includes(suffix ?? '') ? 50 : 10
    if (candidate.size > maxBytes * 1024 * 1024) {
      onFile(null)
      onError(`File is larger than the ${maxBytes} MB local demo limit.`)
      return
    }
    onFile(candidate)
  }

  return (
    <section className="panel" aria-labelledby="upload-title">
      <div className="panel-head">
        <div>
          <span className="step-tag">02 / OR UPLOAD</span>
          <h2 id="upload-title">Your SAR image</h2>
        </div>
      </div>
      <p className="panel-sub">{pngPrototype
        ? 'Upload one 256×256 grayscale PNG tile from the paired dataset. It is duplicated into two model channels; it is not a separate VV/VH model.'
        : 'Two-band Sentinel-1 GeoTIFF (VV band 1, VH band 2), or PNG/JPEG preview, up to 50 MB (GeoTIFF) / 10 MB (preview). Preview images are duplicated across channels and are not true dual-pol input.'}</p>
      <div
        className={`dropzone ${dragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); if (!disabled) accept(e.dataTransfer.files[0]) }}
      >
        <input
          ref={inputRef}
          type="file"
          accept={pngPrototype ? ".png,image/png" : "image/png,image/jpeg,image/tiff,.tif,.tiff"}
          hidden
          onChange={(e) => { accept(e.target.files?.[0]); e.target.value = '' }}
        />
        {file ? (
          <div className="file-row">
            <FileImage size={22} />
            <div><strong>{file.name}</strong><small>{(file.size / 1024 / 1024).toFixed(2)} MB · ready to interpret</small></div>
            <button className="icon-btn" onClick={() => onFile(null)} disabled={disabled} aria-label="Remove file"><X size={18} /></button>
          </div>
        ) : (
          <button className="dropzone-button" onClick={() => inputRef.current?.click()} disabled={disabled}>
            <span className="drop-icon"><Upload size={20} /></span>
            <span><strong>Tap to choose an image</strong><small>or drag &amp; drop here</small></span>
          </button>
        )}
      </div>
    </section>
  )
}
