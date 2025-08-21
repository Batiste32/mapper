import { useState } from "react";
import LoginPanel from "./LoginPanel";
import UploadFilePanel from "./UploadFilePanel";
import Mapper from "./Mapper";

export default function App() {
  const [username, setUsername] = useState<string | null>(null);
  const [password, setPassword] = useState<string | null>(null);
  const [viewUpload, setViewUpload] = useState(false);
  const [hasDatabase, setHasDatabase] = useState(false);

  if (!username || !password) {
    return (
      <LoginPanel
        setUsername={setUsername}
        setPassword={setPassword}
        setHasDatabase={setHasDatabase}
      />
    );
  }

  if (!hasDatabase || viewUpload) {
    return (
      <UploadFilePanel
        username={username}
        password={password}
        setHasDatabase={setHasDatabase}
        switchPanel={() => setViewUpload(false)}
      />
    );
  }

  return <Mapper goBack={() => setViewUpload(true)} />;
}
