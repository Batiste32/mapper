import { useState } from "react";

import LoadingButton from "./components/LoadingButton";

type Props = {
  username: string;
  password: string;
  setHasDatabase: (b: boolean) => void;
  switchPanel: () => void;
};

export default function UploadFilePanel({ username, password, setHasDatabase, switchPanel }: Props) {
  const [fileType, setFileType] = useState<"csv" | "db">("db");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileLoading, setFileLoading] = useState(false);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setSelectedFile(file);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert("Please select a file first.");
      return;
    }

    setFileLoading(true);
    const formData = new FormData();
    formData.append("file", selectedFile);

    if (fileType === "db") {
      formData.append("username", username);
      formData.append("password", password);
    }

    const endpoint =
      fileType === "csv"
        ? `${import.meta.env.VITE_API_BASE}/upload_csv`
        : `${import.meta.env.VITE_API_BASE}/upload_db`;

    try {
      const res = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Upload failed");
      }

      const data = await res.json();
      console.log(`Uploaded ${fileType} response:`, data);

      if (fileType === "csv") {
        setHasDatabase(false); // CSV doesn’t affect DB state
      } else {
        setHasDatabase(true); // once DB uploaded, continue to mapper
      }

      alert("Upload successful!");
      setSelectedFile(null);
    } catch (err) {
      console.error("Upload error:", err);
      alert("Upload failed.");
    } finally {
      setFileLoading(false);
    }
  };

  return (
    <div className="p-4 bg-purple rounded shadow-md mb-6">
      <h2 className="text-lg font-bold mb-2">Upload Files</h2>

      {/* File type selector */}
      <label className="block mb-2 font-medium">Select file type:</label>
      <select
        value={fileType}
        onChange={(e) => {
          setFileType(e.target.value as "csv" | "db");
          setSelectedFile(null);
        }}
        className="border px-3 py-2 mb-4 rounded w-full bg-lavender"
      >
        <option value="csv">CSV File</option>
        <option value="db">SQLite Database (.db)</option>
      </select>

      {/* File input */}
      <input
        type="file"
        accept={fileType === "csv" ? ".csv" : ".db"}
        onChange={handleFileSelect}
        className="border px-3 py-2 mb-4 rounded w-full bg-lavender"
      />

      <div className="flex flex-row">

        <LoadingButton text="Upload File" loadingParameter={fileLoading} onClick={handleUpload} />

        <button
          onClick={switchPanel}
          disabled={fileLoading}
          className={`flex flex-1 p-4 m-2 rounded text-white justify-center items-center
            ${fileLoading ? "bg-lavender opacity-50 cursor-wait" : "bg-midnight hover:bg-lavender"}`}
        >
          Proceed to Mapper
        </button>
      </div>
    </div>
  );
}
