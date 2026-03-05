import { describe, it, expect } from "vitest";
import { existsSync, statSync, readFileSync } from "fs";
import { resolve } from "path";

describe("Distribution", () => {
  describe("A user can build the tool using a build script", () => {
    const buildScriptPath = resolve(process.cwd(), "scripts/build.sh");

    it("the build script exists", () => {
      expect(existsSync(buildScriptPath)).toBe(true);
    });

    it("the build script is executable", () => {
      const stats = statSync(buildScriptPath);
      const isExecutable = !!(stats.mode & 0o100);
      expect(isExecutable).toBe(true);
    });

    it("the build script compiles the tool", () => {
      const content = readFileSync(buildScriptPath, "utf-8");
      expect(content).toContain("npm run build");
    });
  });
});
