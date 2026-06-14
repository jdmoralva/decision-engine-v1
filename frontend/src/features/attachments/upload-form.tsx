import { useState } from "react";


type UploadFormProps = {
  disabled?: boolean;
  onUpload: (file: File) => Promise<void>;
};


export function UploadForm({ disabled = false, onUpload }: UploadFormProps) {
  const [file, setFile] = useState<File | null>(null);

  async function handleUpload() {
    if (file === null) {
      return;
    }
    await onUpload(file);
    setFile(null);
  }

  return (
    <div className="tab-strip">
      <input
        name="attachmentFile"
        type="file"
        accept=".zip,application/zip"
        onChange={(event) => setFile(event.target.files?.[0] ?? null)}
      />
      <button className="secondary-button" type="button" disabled={disabled || file === null} onClick={handleUpload}>
        Cargar ZIP
      </button>
    </div>
  );
}
