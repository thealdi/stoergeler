module.exports = {
  branches: ["main"],
  tagFormat: "frontend-v${version}",
  plugins: [
    [
      "@semantic-release/commit-analyzer",
      {
        preset: "angular",
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
