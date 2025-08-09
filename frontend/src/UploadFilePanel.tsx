import { useState } from "react";

type Props = {
  sqlLoaded: boolean;
  csvLoaded: boolean;
  setSqlLoaded: (v: boolean) => void;
  setCsvLoaded: (v: boolean) => void;
  proceed: () => void;
};

export default function UploadFilePanel({ sqlLoaded, csvLoaded, setSqlLoaded, setCsvLoaded, proceed }: Props) {
  const [fileType, setFileType] = useState<"csv" | "db">("csv");

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    const endpoint =
      fileType === "csv"
        ? `${import.meta.env.VITE_API_BASE}/upload_csv`
        : `${import.meta.env.VITE_API_BASE}/upload_db`;

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      console.log(`Uploaded ${fileType} response:`, data);

      if (fileType === "csv") setCsvLoaded(true);
      else setSqlLoaded(true);

      alert("Upload successful!");
    } catch (err) {
      console.error("Upload error:", err);
      alert("Upload failed.");
    }
  };

  return (
    <div className="p-4 bg-purple rounded shadow-md mb-6">
      <h2 className="text-lg font-bold mb-2">Upload Files</h2>

      {/* Status indicators */}
      <div className="mb-4">
        <p>CSV file loaded: <span className={csvLoaded ? "text-green-500" : "text-red-500"}>{csvLoaded ? "Yes" : "No"}</span></p>
        <p>SQL file loaded: <span className={sqlLoaded ? "text-green-500" : "text-red-500"}>{sqlLoaded ? "Yes" : "No"}</span></p>
      </div>

      {/* File type selector */}
      <label className="block mb-2 font-medium">Select file type:</label>
      <select title="File type selection"
        value={fileType}
        onChange={(e) => setFileType(e.target.value as "csv" | "db")}
        className="border px-3 py-2 mb-4 rounded w-full bg-lavender"
      >
        <option value="csv">CSV File</option>
        <option value="db">SQLite Database (.db)</option>
      </select>

      {/* File upload */}
      <input title="File upload input"
        type="file"
        accept={fileType === "csv" ? ".csv" : ".db"}
        onChange={handleUpload}
        className="border px-3 py-2 mb-4 rounded w-full bg-lavender"
      />

      {/* Proceed button */}
      <button title="Submit file button"
        onClick={proceed}
        disabled={!csvLoaded || !sqlLoaded}
        className={`px-4 py-2 rounded text-white ${csvLoaded && sqlLoaded ? "bg-green-600" : "bg-gray-400 cursor-not-allowed"}`}
      >
        Proceed to Mapper
      </button>
    </div>
  );
}