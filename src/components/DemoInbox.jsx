import { useEffect, useState } from "react";

import { IS_DEMO, demoInbox } from "../api/client";

/**
 * Demo build only: no email is sent, so the code that would have been mailed
 * is shown here. `refresh` changes whenever a new code may have been sent.
 */
function DemoInbox({ email, refresh }) {
  const [mail, setMail] = useState(null);

  useEffect(() => {
    if (!IS_DEMO || !email) return undefined;
    let active = true;
    demoInbox(email).then((m) => active && setMail(m));
    return () => {
      active = false;
    };
  }, [email, refresh]);

  if (!IS_DEMO || !mail) return null;
  return (
    <div className="demo-inbox" role="note">
      <span className="material-symbols-outlined" aria-hidden="true">mail</span>
      <span>
        Demo version: no email is sent. Your code is <strong>{mail.code}</strong>
      </span>
    </div>
  );
}

export default DemoInbox;
