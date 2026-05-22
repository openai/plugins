import { chromium } from "playwright";

async function main() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto("file:///ABSOLUTE/PATH/TO/report.html", {
    waitUntil: "networkidle",
  });
  await page.pdf({
    path: "report.pdf",
    format: "Letter",
    printBackground: true,
    margin: { top: "16mm", right: "16mm", bottom: "16mm", left: "16mm" },
  });
  await browser.close();
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
