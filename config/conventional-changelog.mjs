const TYPE_TITLES = {
  feat: "Features",
  fix: "Bug Fixes",
  perf: "Performance Improvements",
  refactor: "Refactors",
  docs: "Documentation",
  test: "Tests",
  chore: "Chores",
};

export default async function createConfig() {
  return {
    parserOpts: {
      headerPattern: /^(\w*)(?:\((.*)\))?: (.*)$/,
      headerCorrespondence: ["type", "scope", "subject"],
      noteKeywords: ["BREAKING CHANGE", "BREAKING CHANGES"],
    },
    writerOpts: {
      groupBy: "type",
      commitGroupsSort: "title",
      commitsSort: ["scope", "subject"],
      transform: (commit) => {
        if (!commit.type) {
          return commit;
        }
        const title = TYPE_TITLES[commit.type];
        return {
          ...commit,
          type: title || commit.type,
        };
      },
    },
  };
}
