import { useState } from "react";

type Props = {
  sqlLoaded: boolean;
  csvLoaded: boolean;
  setSqlLoaded: (v: boolean) => void;
  setCsvLoaded: (v: boolean) => void;
  proceed: () => void;
};

export default function UploadFilePanel({
  sqlLoaded,
  csvLoaded,
  setSqlLoaded,
  setCsvLoaded,
  proceed,
}: Props) {
  const [fileType, setFileType] = useState<"csv" | "db">("csv");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Step 1: Just store the file when selected
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setSelectedFile(file);
  };

  // Step 2: Upload when clicking the button
  const handleUpload = async () => {
    if (!selectedFile) {
      alert("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

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
      setSelectedFile(null);
    } catch (err) {
      console.error("Upload error:", err);
      alert("Upload failed.");
    }
  };

  return (
    <div className="p-4 bg-purple rounded shadow-md mb-6">
      <h2 className="text-lg font-bold mb-2">Upload Files</h2>

      <div className="mb-4">
        <p className="bg-lavender m-4 p-4 rounded">
          CSV file loaded:{" "}
          <span className={csvLoaded ? "text-green-500" : "text-red-500"}>
            {csvLoaded ? "🟢" : "🔴"}
          </span>
        </p>
        <p className="bg-lavender m-4 p-4 rounded">
          SQL file loaded:{" "}
          <span className={sqlLoaded ? "text-green-500" : "text-red-500"}>
            {sqlLoaded ? "🟢" : "🔴"}
          </span>
        </p>
      </div>

      <label className="block mb-2 font-medium">Select file type:</label>
      <select
        value={fileType}
        onChange={(e) => {
          setFileType(e.target.value as "csv" | "db");
          setSelectedFile(null); // reset selected file if type changes
        }}
        className="border px-3 py-2 mb-4 rounded w-full bg-lavender"
      >
        <option value="csv">CSV File</option>
        <option value="db">SQLite Database (.db)</option>
      </select>

      <input
        type="file"
        accept={fileType === "csv" ? ".csv" : ".db"}
        onChange={handleFileSelect}
        className="border px-3 py-2 mb-4 rounded w-full bg-lavender"
      />
      <div id="upload_buttons" className="flex">
        <button
          onClick={handleUpload}
          disabled={!selectedFile}
          className={`flex-1 p-4 m-4 rounded text-white ${ selectedFile ? "bg-midnight hover:bg-lavender" : "bg-dark cursor-not-allowed" }`}
        >
          Upload File
        </button>
        <button
          onClick={proceed}
          className={`flex-1 p-4 m-4 rounded text-white ${ csvLoaded && sqlLoaded ? "bg-midnight hover:bg-lavender" : "bg-dark cursor-not-allowed" }`}
          /*disabled={!csvLoaded || !sqlLoaded}*/
        >
          Proceed to Mapper
        </button>
      </div>
    </div>
  );
}
