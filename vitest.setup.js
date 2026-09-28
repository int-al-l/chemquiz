import "@testing-library/jest-dom/vitest";

import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// Testing Library only registers its own cleanup when Vitest globals are on.
// They are off here, so unmount between tests explicitly -- otherwise every
// render stacks up in the same document and queries find several matches.
afterEach(cleanup);
