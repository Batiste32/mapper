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
};

type ProfilePanelProps = {
  selectedProfile: Profile | null;
};

export default function ProfilePanel({ selectedProfile }: ProfilePanelProps) {
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
            <div className="m-3" key={k}>
              <p>
                <strong>{k}</strong>: {v ?? "N/A"}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <p>No profile selected.</p>
      )}
    </div>
  );
}
