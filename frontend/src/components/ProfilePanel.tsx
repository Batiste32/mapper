type Profile = {
  index: number;
  array_id: string;
  name: string;
  personality: string;
  arguments: string;
  nbhood: string;
  preferred_language: string;
  origin: string;
  political_scale: string;
  ideal_process: string;
  strategic_profile: string;
  picture_url: string;
};

type ProfilePanelProps = {
  selectedProfile: Profile | null;
};

export default function ProfilePanel({ selectedProfile }: ProfilePanelProps) {

  const format_aliases: Record<string, string> = {
    origin: "Ethnicity",
    political_lean: "Political Alignment",
    score_vote: "Voting Score",
    nbhood: "Neighborhood",
    preferred_language: "Preferred Language",
    ideal_process: "Ideal Process",
    strategic_profile: "Strategic Profile",
    uniqueid: "Unique ID",
    political_scale: "Political Analysis"
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

  function renderValue(value: string) {
    if (!value) return null;
    const lower = value.toLowerCase();
    const isImage = lower.endsWith(".jpg") || lower.endsWith(".jpeg") || lower.endsWith(".png") || lower.endsWith(".gif") || lower.endsWith(".webp");

    if (isImage) {
      console.log("Detected Image for value :",value)
      return (
        <img
          src={value}
          alt="Profile"
          className="max-w-full max-h-64 rounded shadow"
        />
      );
    }

    return <span>{value}</span>;
  }

  return (
    <div
      className={`w-full p-4 bg-midnight border-t sm:border-t-0 sm:border-l max-h-[30vh] sm:max-h-none overflow-auto z-10
        transition-all duration-300 ease-in-out
        ${selectedProfile ? "sm:w-1/2" : "sm:w-64"}`}
    >
      <h2 className="text-xl font-semibold mb-4">Profile Info</h2>
      {selectedProfile ? (
        <div>
          {Object.entries(selectedProfile).map(([k, v]) => (
            <ul className="m-3" key={k}>
              <li key={k} className="text-sm">
                <span className="font-semibold">{formatLabel(k)}:</span> {renderValue(String(v))}
              </li>
            </ul>
          ))}
        </div>
      ) : (
        <p>No profile selected.</p>
      )}
    </div>
  );
}
