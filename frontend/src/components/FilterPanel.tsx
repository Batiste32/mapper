import AutocompleteInput from "./AutocompleteInput";

interface FilterPanelProps {
  filters: any;
  setFilters: React.Dispatch<React.SetStateAction<any>>;
  startAddress: string;
  setStartAddress: (value: string) => void;
  handleSearch: () => void;
  validEthnicities: string[];
  validAlignments: string[];
  mapperWait: boolean;
}

export default function FilterPanel( 
    { filters, setFilters, startAddress, setStartAddress, handleSearch, validEthnicities, validAlignments, mapperWait }: FilterPanelProps ){

    return(
        <div className="flex flex-col sm:w-64 p-4 bg-midnight border-b sm:border-b-0 sm:border-r max-h-[30vh] sm:max-h-none overflow-auto z-10">
            <h2 className="flex-1 text-xl font-semibold mb-4">Filters</h2>
            <AutocompleteInput label="Ethnicity" value={filters.ethnicity} onChange={(val) => setFilters({ ...filters, ethnicity: val })} suggestions={validEthnicities}/>
            <AutocompleteInput label="Political Alignment" value={filters.political_alignment} onChange={(val) => setFilters({ ...filters, political_alignment: val })} suggestions={validAlignments}/>
            <label className="flex-1 block mb-2">
            Min Vote Score:
            <input
                type="number"
                className="flex-1 w-full border rounded p-1"
                value={filters.min_score_vote}
                onChange={(e) => setFilters({ ...filters, min_score_vote: parseFloat(e.target.value) })}
            />
            </label>
            <label className="flex-1 block mb-2">
            Start Adress :
            <input
            type="text"
            value={startAddress}
            onChange={(e) => setStartAddress(e.target.value)}
            placeholder="(leave blank to use GPS)"
            className="flex-1 border p-2 rounded w-full"
            />
            </label>
            <button
              onClick={handleSearch}
              className={`flex items-center justify-center mt-4 w-full p-2 rounded text-white ${
                mapperWait ? "bg-gray-500 cursor-not-allowed" : "bg-purple hover:bg-lavender"
              }`}
              disabled={mapperWait}
            >
              {mapperWait ? (
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
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                  ></path>
                </svg>
              ) : (
                "Search"
              )}
            </button>
        </div>
      );
    }