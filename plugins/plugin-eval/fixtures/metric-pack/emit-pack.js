const [, , targetPath, targetKind] = process.argv;

console.log(
  JSON.stringify({
    checks: [
      {
        id: "custom-target-kind",
        category: "custom",
        severity: "info",
        status: "info",
        message: `Metric pack saw ${targetKind}`,
        evidence: [targetPath],
        remediation: []
      }
    ],
    metrics: [
      {
        id: "custom-pack-score",
        category: "custom",
        value: 7,
        unit: "points",
        band: "good"
      }
    ],
    artifacts: [
      {
        id: "custom-pack-artifact",
        type: "custom",
        label: "Custom pack artifact",
        description: "Simple fixture artifact"
      }
    ]
  })
);
