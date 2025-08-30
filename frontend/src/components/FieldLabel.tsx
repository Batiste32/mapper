import { useEffect, useState } from "react";

type FieldMetadata = {
  field_name: string;
  label: string | null;
  description: string | null;
};

type Props = {
  field: string;
  API_BASE?: string; 
};

  const format_aliases: Record<string, string> = {
    origin: "Ethnicity",
    political_lean: "Political Alignment",
    score_vote: "Voting Score",
    nbhood: "Neighborhood",
    preferred_language: "Preferred Language",
    ideal_process: "Ideal Process",
    strategic_profile: "Strategic Profile",
    uniqueid: "Text ID"
  };

  function formatLabel(key: string): string {
    // Use alias if defined
    if (format_aliases[key]) return format_aliases[key];

    // Otherwise apply casing
    return key
      .replace(/_/g, " ")
      .replace(/\w\S*/g, (w) => 
        w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()
      );
  }

export default function FieldLabel({ field, API_BASE = import.meta.env.VITE_API_BASE }: Props) {
  const [metadata, setMetadata] = useState<FieldMetadata | null>(null);
  const [showTooltip, setShowTooltip] = useState(false);

  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const res = await fetch(`${API_BASE}/profiles/field_metadata/${field}`, {
          headers: { "ngrok-skip-browser-warning": "true" },
        });
        if (!res.ok) throw new Error("Failed to fetch metadata");
        const data = await res.json();
        setMetadata(data);
      } catch (err) {
        console.error("Failed to load metadata:", err);
        setMetadata({ field_name: field, label: null, description: null });
      }
    };
    fetchMetadata();
  }, [field, API_BASE]);

  const label = metadata?.label || formatLabel(field);
  const description = metadata?.description || "No description available.";

  const toggleTooltip = () => setShowTooltip((prev) => !prev);

  return (
    <div className="relative inline-block">
      <span
        className="cursor-help underline decoration-dotted"
        onClick={toggleTooltip}            // mobile 
        onMouseEnter={() => setShowTooltip(true)}  // desktop 
        onMouseLeave={() => setShowTooltip(false)} // desktop 
      >
        {label}
      </span>

      {showTooltip && description && (
        <div
          className="absolute z-50 mt-2 w-64 p-2 rounded-md bg-gray-800 text-white text-sm shadow-lg"
          style={{ left: "50%", transform: "translateX(-50%)" }}
        >
          {description}
        </div>
      )}
    </div>
  );
}