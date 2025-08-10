import { useState} from "react";

import Mapper from "./Mapper";
import UploadFilePanel from "./UploadFilePanel";

import './App.css'

export default function App() {
  const [sqlLoaded, setSqlLoaded] = useState<boolean>(false);
  const [csvLoaded, setCsvLoaded] = useState<boolean>(false);
  const [view, setView] = useState<"upload" | "mapper">("upload");
  return (
    <>
      <h1 className="text-2xl font-bold m-4 bg-purple p-4 rounded">Intelligent Mapper</h1>
      {view === "upload" && (
        <UploadFilePanel
          sqlLoaded={sqlLoaded}
          csvLoaded={csvLoaded}
          setSqlLoaded={setSqlLoaded}
          setCsvLoaded={setCsvLoaded}
          proceed={() => setView("mapper")}
        />
      )}
      {view === "mapper" && (
        <Mapper goBack={() => setView("upload")} />
      )}
    </>
  );
}
