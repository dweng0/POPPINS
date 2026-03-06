import React from "react";
import { render } from "ink-testing-library";
import { describe, it, expect, vi } from "vitest";
import App from "../src/app.js";
import * as fs from "fs";

vi.mock("fs", async (importOriginal) => {
  const actual = await importOriginal<typeof import("fs")>();
  return {
    ...actual,
    writeFileSync: vi.fn(),
  };
});

const ENTER = "\r";
const ESCAPE = "\u001B";

function typeText(stdin: { write: (s: string) => void }, text: string) {
  for (const char of text) {
    stdin.write(char);
  }
}

function submit(stdin: { write: (s: string) => void }, text: string) {
  typeText(stdin, text);
  stdin.write(ENTER);
}

describe("BDD Wizard", () => {
  it("allow a user to specify the language", async () => {
    const { lastFrame, stdin } = render(<App outputPath="/tmp/test-bdd.md" />);
    expect(lastFrame()).toContain("programming language");
    submit(stdin, "typescript");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("framework");
  });

  it("allow a user to specify the framework", async () => {
    const { lastFrame, stdin } = render(<App outputPath="/tmp/test-bdd.md" />);
    submit(stdin, "typescript");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("framework");
    submit(stdin, "react");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Build command");
  });

  it("allow a user to optionally specify the build command", async () => {
    const { lastFrame, stdin } = render(<App outputPath="/tmp/test-bdd.md" />);
    submit(stdin, "typescript");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "react");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Build command");
    submit(stdin, "npm run build");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Test command");
  });

  it("allow a user to not need to provide a build command", async () => {
    const mockWriteFileSync = vi.mocked(fs.writeFileSync);
    mockWriteFileSync.mockClear();

    const { lastFrame, stdin } = render(<App outputPath="/tmp/test-bdd.md" />);
    submit(stdin, "typescript");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "react");
    await new Promise((r) => setTimeout(r, 50));
    // Press enter with no input to auto-detect
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Test command");
    // Continue through wizard to completion and verify build cmd was inferred
    stdin.write(ENTER); // test_cmd blank
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER); // lint_cmd blank
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER); // fmt_cmd blank
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER); // system description blank
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "done");
    await new Promise((r) => setTimeout(r, 150));
    expect(mockWriteFileSync).toHaveBeenCalled();
    const content = mockWriteFileSync.mock.calls[0]?.[1] as string;
    expect(content).toContain("build_cmd: tsc");
  });

  it("allow a user to optionally specify the test command", async () => {
    const { lastFrame, stdin } = render(<App outputPath="/tmp/test-bdd.md" />);
    submit(stdin, "typescript");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "react");
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER); // build_cmd blank
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Test command");
    submit(stdin, "jest");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Lint command");
  });

  it("allow a user to not need to provide a test command", async () => {
    const mockWriteFileSync = vi.mocked(fs.writeFileSync);
    mockWriteFileSync.mockClear();

    const { lastFrame, stdin } = render(<App outputPath="/tmp/test-bdd.md" />);
    submit(stdin, "typescript");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "react");
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER); // build_cmd blank
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER); // test_cmd blank - should auto-detect
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Lint command");
    stdin.write(ENTER); // lint_cmd blank
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER); // fmt_cmd blank
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER); // system description blank
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "done");
    await new Promise((r) => setTimeout(r, 150));
    expect(mockWriteFileSync).toHaveBeenCalled();
    const content = mockWriteFileSync.mock.calls[0]?.[1] as string;
    expect(content).toContain("test_cmd: npm test");
  });

  it("allow a user to optionally specify the lint command", async () => {
    const { lastFrame, stdin } = render(<App outputPath="/tmp/test-bdd.md" />);
    submit(stdin, "typescript");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "react");
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Lint command");
    submit(stdin, "eslint .");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Format command");
  });

  it("allow a user to not need to provide a lint command", async () => {
    const mockWriteFileSync = vi.mocked(fs.writeFileSync);
    mockWriteFileSync.mockClear();

    const { stdin } = render(<App outputPath="/tmp/test-bdd.md" />);
    submit(stdin, "typescript");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "react");
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER); // lint_cmd blank - auto-detect
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER); // fmt_cmd blank
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER); // system description blank
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "done");
    await new Promise((r) => setTimeout(r, 150));
    expect(mockWriteFileSync).toHaveBeenCalled();
    const content = mockWriteFileSync.mock.calls[0]?.[1] as string;
    expect(content).toContain("lint_cmd: eslint .");
  });

  it("allow a user to optionally specify the format command", async () => {
    const { lastFrame, stdin } = render(<App outputPath="/tmp/test-bdd.md" />);
    submit(stdin, "typescript");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "react");
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Format command");
    submit(stdin, "prettier --write .");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("system");
  });

  it("allow a user to not need to provide a format command", async () => {
    const mockWriteFileSync = vi.mocked(fs.writeFileSync);
    mockWriteFileSync.mockClear();

    const { stdin } = render(<App outputPath="/tmp/test-bdd.md" />);
    submit(stdin, "typescript");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "react");
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER); // fmt_cmd blank - auto-detect
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER); // system description blank
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "done");
    await new Promise((r) => setTimeout(r, 150));
    expect(mockWriteFileSync).toHaveBeenCalled();
    const content = mockWriteFileSync.mock.calls[0]?.[1] as string;
    expect(content).toContain("fmt_cmd: prettier --write .");
  });

  it("the birthdate of the project should be added to the frontmatter of the bdd file", async () => {
    const mockWriteFileSync = vi.mocked(fs.writeFileSync);
    mockWriteFileSync.mockClear();

    const { stdin } = render(<App outputPath="/tmp/test-bdd.md" />);
    submit(stdin, "typescript");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "react");
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER); // system description
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "done");
    await new Promise((r) => setTimeout(r, 150));
    expect(mockWriteFileSync).toHaveBeenCalled();
    const content = mockWriteFileSync.mock.calls[0]?.[1] as string;
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, "0");
    const day = String(today.getDate()).padStart(2, "0");
    expect(content).toContain(`birth_date: ${year}-${month}-${day}`);
  });

  it("the user should be able to not provide a system description through user input", async () => {
    const mockWriteFileSync = vi.mocked(fs.writeFileSync);
    mockWriteFileSync.mockClear();

    const { lastFrame, stdin } = render(<App outputPath="/tmp/test-bdd.md" />);
    submit(stdin, "typescript");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "react");
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("system");
    stdin.write(ENTER); // skip system description
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "done");
    await new Promise((r) => setTimeout(r, 150));
    expect(mockWriteFileSync).toHaveBeenCalled();
    const content = mockWriteFileSync.mock.calls[0]?.[1] as string;
    expect(content).not.toContain("System:");
  });

  it("adding features to the bdd file through user input", async () => {
    const mockWriteFileSync = vi.mocked(fs.writeFileSync);
    mockWriteFileSync.mockClear();

    const { lastFrame, stdin } = render(<App outputPath="/tmp/test-bdd.md" />);
    // frontmatter
    submit(stdin, "typescript");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "react");
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER); // system description
    await new Promise((r) => setTimeout(r, 50));
    // Now at feature_or_done
    expect(lastFrame()).toContain("feature");
    // type a feature name and press enter (goes to feature_name step)
    submit(stdin, "add");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Feature name");
    submit(stdin, "User Authentication");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("scenario");
  });

  it("a user wants to be able to provide a scenario for a feature through user input", async () => {
    const mockWriteFileSync = vi.mocked(fs.writeFileSync);
    mockWriteFileSync.mockClear();

    const { lastFrame, stdin } = render(<App outputPath="/tmp/test-bdd.md" />);
    submit(stdin, "typescript");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "react");
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    // feature_or_done
    submit(stdin, "add");
    await new Promise((r) => setTimeout(r, 50));
    // feature_name
    submit(stdin, "Login");
    await new Promise((r) => setTimeout(r, 50));
    // feature_action
    submit(stdin, "s");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Scenario name");
    submit(stdin, "User logs in");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Given");
    submit(stdin, "the user has an account");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("When");
    submit(stdin, "the user enters credentials");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Then");
    submit(stdin, "the user is logged in");
    await new Promise((r) => setTimeout(r, 50));
    // back to feature_action
    expect(lastFrame()).toContain("scenario");
    // done with feature
    submit(stdin, "d");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "done");
    await new Promise((r) => setTimeout(r, 150));
    expect(mockWriteFileSync).toHaveBeenCalled();
    const content = mockWriteFileSync.mock.calls[0]?.[1] as string;
    expect(content).toContain("Scenario: User logs in");
    expect(content).toContain("Given the user has an account");
    expect(content).toContain("When the user enters credentials");
    expect(content).toContain("Then the user is logged in");
  });

  it("a user should be able to add 0 or more backgrounds to a feature through user input", async () => {
    const mockWriteFileSync = vi.mocked(fs.writeFileSync);
    mockWriteFileSync.mockClear();

    const { lastFrame, stdin } = render(<App outputPath="/tmp/test-bdd.md" />);
    submit(stdin, "typescript");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "react");
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "add");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "Auth Feature");
    await new Promise((r) => setTimeout(r, 50));
    // Add background
    submit(stdin, "b");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Background Given");
    submit(stdin, "the database is seeded");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("scenario");
    // Done with feature
    submit(stdin, "d");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "done");
    await new Promise((r) => setTimeout(r, 150));
    expect(mockWriteFileSync).toHaveBeenCalled();
    const content = mockWriteFileSync.mock.calls[0]?.[1] as string;
    expect(content).toContain("Background:");
    expect(content).toContain("Given the database is seeded");
  });

  it("adding scenarios to the feature through user input", async () => {
    const mockWriteFileSync = vi.mocked(fs.writeFileSync);
    mockWriteFileSync.mockClear();

    const { lastFrame, stdin } = render(<App outputPath="/tmp/test-bdd.md" />);
    submit(stdin, "python");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "django");
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "add");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "Shopping Cart");
    await new Promise((r) => setTimeout(r, 50));
    // Add first scenario (guided input)
    submit(stdin, "s");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Scenario name");
    submit(stdin, "Add item to cart");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Given");
    submit(stdin, "the user is logged in");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("When");
    submit(stdin, "the user clicks add to cart");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Then");
    submit(stdin, "the item is in the cart");
    await new Promise((r) => setTimeout(r, 50));
    // Back to feature action - add another scenario
    submit(stdin, "s");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "Remove item from cart");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "the user has items in cart");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "the user clicks remove");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "the cart is empty");
    await new Promise((r) => setTimeout(r, 50));
    // Done
    submit(stdin, "d");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "done");
    await new Promise((r) => setTimeout(r, 150));
    expect(mockWriteFileSync).toHaveBeenCalled();
    const content = mockWriteFileSync.mock.calls[0]?.[1] as string;
    expect(content).toContain("Scenario: Add item to cart");
    expect(content).toContain("Scenario: Remove item from cart");
  });

  it("cancelling adding a scenario to the feature through user input", async () => {
    const { lastFrame, stdin } = render(<App outputPath="/tmp/test-bdd.md" />);
    submit(stdin, "typescript");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "react");
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "add");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "My Feature");
    await new Promise((r) => setTimeout(r, 50));
    // Start adding scenario
    submit(stdin, "s");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Scenario name");
    // Go to scenario_given
    submit(stdin, "Test scenario");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Given");
    // Press escape to go back to scenario_name
    stdin.write(ESCAPE);
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Scenario name");
    // Press escape again to go back to feature_action
    stdin.write(ESCAPE);
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("scenario");
  });

  it("cancelling adding a background to the feature through user input", async () => {
    const { lastFrame, stdin } = render(<App outputPath="/tmp/test-bdd.md" />);
    submit(stdin, "typescript");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "react");
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "add");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "My Feature");
    await new Promise((r) => setTimeout(r, 50));
    // Start adding background
    submit(stdin, "b");
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("Background Given");
    // Press escape to go back to feature_action
    stdin.write(ESCAPE);
    await new Promise((r) => setTimeout(r, 50));
    expect(lastFrame()).toContain("scenario");
  });

  it("completing the bdd", async () => {
    const mockWriteFileSync = vi.mocked(fs.writeFileSync);
    mockWriteFileSync.mockClear();

    const { lastFrame, stdin } = render(<App outputPath="/tmp/out.md" />);
    submit(stdin, "go");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "gin");
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    stdin.write(ENTER);
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "My system");
    await new Promise((r) => setTimeout(r, 50));
    submit(stdin, "done");
    await new Promise((r) => setTimeout(r, 150));
    expect(mockWriteFileSync).toHaveBeenCalled();
    expect(lastFrame()).toContain("BDD file created successfully");
    expect(lastFrame()).toContain("out.md");
  });
});
