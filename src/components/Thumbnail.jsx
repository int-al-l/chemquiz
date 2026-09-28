import { useState } from "react";

import { imageSrc } from "../api/client";

/**
 * A glassware picture, falling back to the old grey placeholder when an item
 * has no image or the file fails to load. Content is arriving a page at a time
 * from the catalog, so a missing image is a normal state, not a bug.
 */
function Thumbnail({ imageUrl, alt = "", className = "" }) {
  const [failed, setFailed] = useState(false);
  const src = imageSrc(imageUrl);

  if (!src || failed) {
    return <div className={`thumbnail thumbnail-empty ${className}`} aria-hidden="true" />;
  }

  return (
    <div className={`thumbnail ${className}`}>
      <img src={src} alt={alt} loading="lazy" onError={() => setFailed(true)} />
    </div>
  );
}

export default Thumbnail;
