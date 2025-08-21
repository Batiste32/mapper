import { useEffect, useState } from "react";
import AutocompleteInput from "./AutocompleteInput";

interface FilterPanelProps {
  applyFilters: (filters: Record<string, string>) => void;
}

export default function FilterPanel({ applyFilters }: FilterPanelProps) {
  const [fields, setFields] = useState<{ [key: string]: string }>({});
  const [filters, setFilters] = useState<{ [key: string]: string }>({});
  const [suggestions, setSuggestions] = useState<{ [key: string]: string[] }>({});

  // Fetch available fields on mount
  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_BASE}/profiles/fields`)
      .then((res) => res.json())
      .then((data) => setFields(data));
  }, []);

  // Fetch valid values for categorical fields
  const fetchSuggestions = async (field: string) => {
    if (suggestions[field]) return;
    try {
      const res = await fetch(
        `${import.meta.env.VITE_API_BASE}/profiles/valid_values?field=${field}`
      );
      if (res.ok) {
        const values = await res.json();
        setSuggestions((prev) => ({ ...prev, [field]: values }));
      }
    } catch (err) {
      console.error(`Failed to load suggestions for ${field}`, err);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFilters((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="p-4 bg-purple rounded">
      <h2 className="font-bold text-white">Filters</h2>

      <div className="overflow-y-auto pr-2">
        {Object.entries(fields).map(([field, type]) => (
          <AutocompleteInput
            key={field}
            label={field}
            value={filters[field] || ""}
            onChange={(val) => handleChange(field, val)}
            suggestions={suggestions[field] || []}
            onFocus={() => fetchSuggestions(field)}
          />
        ))}
      </div>
      <button
        onClick={() => applyFilters(filters)}
        className="bg-midnight hover:bg-lavender p-2 mt-4 rounded text-white"
      >
        Apply Filters
      </button>
    </div>
  );
}
