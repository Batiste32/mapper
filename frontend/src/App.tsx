import { useState } from "react";
import LoginPanel from "./LoginPanel";
import UploadFilePanel from "./UploadFilePanel";
import Mapper from "./Mapper";

export default function App() {
  const [username, setUsername] = useState<string | null>(null);
  const [password, setPassword] = useState<string | null>(null);
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

  if (!hasDatabase) {
    return (
      <UploadFilePanel
        username={username}
        password={password}
        setHasDatabase={setHasDatabase}
      />
    );
  }

  return <Mapper username={username} />;
}
