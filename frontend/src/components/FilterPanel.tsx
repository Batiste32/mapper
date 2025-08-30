  import { useEffect, useState } from "react";

  import AutocompleteInput from "./AutocompleteInput";
  import LoadingButton from "./LoadingButton";
  import FieldLabel from "./FieldLabel";

  interface FilterPanelProps {
    applyFilters: (filters: Record<string, string>) => void;
    mapperWait: boolean;
  }

  export default function FilterPanel({ applyFilters, mapperWait }: FilterPanelProps) {
    const [fields, setFields] = useState<{ [key: string]: string }>({});
    const [filters, setFilters] = useState<{ [key: string]: string }>({});
    const [suggestions, setSuggestions] = useState<{ [key: string]: string[] }>({});
    const [startAddress, setStartAddress] = useState("");
    const [addressSuggestions, setAddressSuggestions] = useState<any[]>([]);

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

    // Fetch available fields on mount
    useEffect(() => {
      fetch(`${import.meta.env.VITE_API_BASE}/profiles/fields`)
        .then((res) => res.json())
        .then((data) => setFields(data));
    }, []);

    useEffect(() => {
      const handleReset = () => {
        setFilters({});
        setStartAddress("");
      };

      window.addEventListener("reset-filters", handleReset);
      return () => window.removeEventListener("reset-filters", handleReset);
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

    const fetchGeocode = async (query: string) => {
      if (!query) {
        setAddressSuggestions([]);
        return;
      }
      try {
        const res = await fetch(
          `${import.meta.env.VITE_API_BASE}/geocode?q=${encodeURIComponent(query)}`
        );
        if (res.ok) {
          const data = await res.json();
          setAddressSuggestions(data);
        }
      } catch (err) {
        console.error("Failed to fetch geocode suggestions", err);
      }
    };

    const handleSelectAddress = (val: any) => {
      setStartAddress(val.display_name);
      setFilters((prev) => ({
        ...prev,
        start_lat: val.lat,
        start_lon: val.lon,
      }));
      setAddressSuggestions([]);
    };

    return (
      <div id="filter-main" className="p-4 bg-purple rounded h-1/3 sm:h-full md:h-full lg:h-full flex flex-col">
        <h2 className="font-bold text-white">Filters</h2>
        <div id="start-address" className="relative mb-4">
          <label className="block text-sm font-medium mb-1">Start Address</label>
          <input
            type="text"
            value={startAddress}
            onChange={(e) => {
              setStartAddress(e.target.value);
              fetchGeocode(startAddress);
            }}
            className="w-full border px-3 py-2 rounded"
            placeholder="Enter start address"
          />
          {addressSuggestions.length > 0 && (
            <ul className="absolute z-10 bg-purple border rounded w-full max-h-40 overflow-y-auto mt-1">
              {addressSuggestions.map((addr) => (
                <li
                  key={addr.place_id}
                  className="px-3 py-2 hover:bg-lavender cursor-pointer"
                  onMouseDown={() => handleSelectAddress(addr)}
                >
                  {addr.display_name}
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="overflow-y-auto pr-2">
          {Object.entries(fields).map(([field, type]) => (
            <>
              <FieldLabel field={field} filter_visible_check={true} />
              <AutocompleteInput
                key={field}
                value={filters[field] || ""}
                onChange={(val) => handleChange(field, val)}
                suggestions={suggestions[field] || []}
                onFocus={() => fetchSuggestions(field)}
              />
            </>
          ))}
        </div>
        <LoadingButton onClick={()=>applyFilters(filters)} text="Apply Filters" loadingParameter={mapperWait} />
      </div>
    );
  }
