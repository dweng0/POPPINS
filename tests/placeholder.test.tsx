import React from "react";
import { render } from "ink-testing-library";
import { describe, it, expect } from "vitest";
import App from "../src/app.js";

describe("placeholder", () => {
  it("renders without crashing", () => {
    const { lastFrame } = render(<App />);
    expect(lastFrame()).toContain("Hello");
  });
});
