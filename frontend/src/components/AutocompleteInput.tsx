import { useState, useRef } from "react";

interface AutocompleteInputProps {
  label: string;
  value: string;
  onChange: (val: string) => void;
  suggestions: string[];
  onFocus?: () => void;
}

const AutocompleteInput: React.FC<AutocompleteInputProps> = ({
  label,
  value,
  onChange,
  suggestions,
  onFocus,
}) => {
  const [showSuggestions, setShowSuggestions] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleBlur = () => {
    timeoutRef.current = setTimeout(() => setShowSuggestions(false), 100);
  };

  const handleFocus = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    if (onFocus) onFocus();
    setShowSuggestions(true);
  };

  const filteredSuggestions = suggestions
    .map((val) => String(val))
    .filter((val) => val.toLowerCase().includes(value.toLowerCase()));

  return (
    <div className="relative mb-4">
      <label className="block text-sm font-medium mb-1">{label}
        <input type="text" className="w-full border px-3 py-2 rounded" value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={handleFocus}
          onBlur={handleBlur}
        />
      </label>
      {showSuggestions && filteredSuggestions.length > 0 && (
        <ul className="absolute z-10 bg-midnight border rounded w-full max-h-40 overflow-y-auto mt-1">
          {filteredSuggestions.map((val) => (
            <li
              key={val}
              className="px-3 py-2 hover:bg-lavender cursor-pointer"
              onMouseDown={() => onChange(val)}
            >
              {val}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default AutocompleteInput;
