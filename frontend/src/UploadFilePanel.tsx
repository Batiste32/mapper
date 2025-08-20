import { useState } from "react";

type Props = {
  sqlLoaded: boolean;
  csvLoaded: boolean;
  setSqlLoaded: (v: boolean) => void;
  setCsvLoaded: (v: boolean) => void;
  proceed: () => void;
  username: string;
  password: string;
};

export default function UploadFilePanel({
  sqlLoaded,
  csvLoaded,
  setSqlLoaded,
  setCsvLoaded,
  proceed,
  username,
  password,
}: Props) {
  const [fileType, setFileType] = useState<"csv" | "db">("csv");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [fileLoading, setFileLoading] = useState<boolean>(false);

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

    // send login info for db files
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

      const data = await res.json();
      console.log(`Uploaded ${fileType} response:`, data);

      if (fileType === "csv") setCsvLoaded(true);
      else setSqlLoaded(true);

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

      {/* Status indicators */}
      <div className="mb-4">
        <p className="bg-lavender m-2 p-2 rounded">
          CSV file loaded:{" "}
          <span className={csvLoaded ? "text-green-500" : "text-red-500"}>
            {csvLoaded ? "🟢" : "🔴"}
          </span>
        </p>
        <p className="bg-lavender m-2 p-2 rounded">
          SQL file loaded:{" "}
          <span className={sqlLoaded ? "text-green-500" : "text-red-500"}>
            {sqlLoaded ? "🟢" : "🔴"}
          </span>
        </p>
      </div>

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

      {/* Upload + Proceed buttons */}
      <div className="flex">
        <button
          onClick={handleUpload}
          disabled={fileLoading || !selectedFile}
          className={`flex flex-1 p-4 m-2 rounded text-white justify-center items-center
            ${
              fileLoading
                ? "bg-lavender opacity-50 cursor-wait"
                : selectedFile
                ? "bg-midnight hover:bg-lavender"
                : "bg-dark cursor-not-allowed"
            }`}
        >
          {fileLoading ? (
            <svg
              className="animate-spin h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
              />
            </svg>
          ) : (
            "Upload File"
          )}
        </button>
        <button
          onClick={proceed}
          className={`flex-1 p-4 m-2 rounded text-white ${
            csvLoaded && sqlLoaded
              ? "bg-midnight hover:bg-lavender"
              : "bg-dark cursor-not-allowed"
          }`}
          disabled={!csvLoaded || !sqlLoaded}
        >
          Proceed to Mapper
        </button>
      </div>
    </div>
  );
}
