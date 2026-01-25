module.exports = {
  branches: ["main"],
  tagFormat: "frontend-v${version}",
  plugins: [
    [
      "@semantic-release/commit-analyzer",
      {
        preset: "angular",
        releaseRules: [
          { scope: "frontend", release: "minor" },
          { scope: "frontend", type: "fix", release: "patch" },
          { scope: "frontend", type: "perf", release: "patch" },
          { scope: "frontend", breaking: true, release: "major" },
        ],
      },
    ],
    [
      "@semantic-release/release-notes-generator",
      {
        preset: "angular",
      },
    ],
    "@semantic-release/github",
  ],
};
