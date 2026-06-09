# SmartBrowz Deep-Dive Reference

## When to use this file
Load this file when the user asks about: SmartBrowz headless browser, Puppeteer/Playwright/Selenium
in Catalyst, Browser Logic functions, Browser Grid, PDF generation, screenshot capture, HTML templates,
LiquidJS templates, or Dataverse APIs.

External docs: https://docs.catalyst.zoho.com/en/serverless/smartbrowz/

---

## Components Overview

| Component | Description | Status |
|-----------|-------------|--------|
| **Headless Browser** | Connect to managed browsers via Puppeteer, Playwright, or Selenium | GA |
| **Browser Logic Functions** | Serverless functions with pre-initialized browser sessions | GA |
| **Browser Grid** | Dedicated browser infrastructure with configurable tiers | Early Access |
| **PDF & Screenshot** | Generate PDFs and screenshots from HTML, URLs, or templates | GA |
| **Templates** | LiquidJS-based HTML templates for dynamic document generation | GA |
| **Dataverse** | Business data enrichment APIs (Lead Enrichment, Tech Stack, Similar Companies) | Beta (US only) |

---

## Headless Browser

Connect to Catalyst-managed headless browsers from your functions using your preferred
automation framework.

### Supported Browsers
- **Chrome** v137
- **Firefox** v136

### Puppeteer (Node.js)

```javascript
const puppeteer = require('puppeteer-core');
const catalyst = require('zcatalyst-sdk-node');

module.exports = async (context, basicIO) => {
  const catalystApp = catalyst.initialize(context);
  const smartBrowz = catalystApp.smartBrowz();
  const browserDetails = await smartBrowz.open();

  const browser = await puppeteer.connect({
    browserWSEndpoint: browserDetails.browser_ws_url
  });

  const page = await browser.newPage();
  await page.goto('https://example.com');
  const title = await page.title();

  await browser.close();
  basicIO.write({ title });
  context.close();
};
```

### Playwright — Node.js

```javascript
const { chromium } = require('playwright');
const catalyst = require('zcatalyst-sdk-node');

module.exports = async (context, basicIO) => {
  const catalystApp = catalyst.initialize(context);
  const smartBrowz = catalystApp.smartBrowz();
  const browserDetails = await smartBrowz.open();

  const browser = await chromium.connectOverCDP(browserDetails.browser_ws_url);
  const defaultContext = browser.contexts()[0];
  const page = defaultContext.pages()[0] || await defaultContext.newPage();

  await page.goto('https://example.com');
  const title = await page.title();

  await browser.close();
  basicIO.write({ title });
  context.close();
};
```

### Playwright — Python

```python
from playwright.sync_api import sync_playwright

def handler(catalyst_app, context, basic_io):
    smart_browz = catalyst_app.smart_browz()
    browser_details = smart_browz.open()

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(browser_details["browser_ws_url"])
        default_context = browser.contexts[0]
        page = default_context.pages[0] if default_context.pages else default_context.new_page()

        page.goto("https://example.com")
        title = page.title()

        browser.close()

    basic_io.write({"title": title})
    context.close()
```

### Selenium — Java

```java
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.remote.RemoteWebDriver;
import java.net.URL;
import org.openqa.selenium.chrome.ChromeOptions;

public class BrowserFunction implements ZCFunction {
    public void runner(CatalystApp catalystApp, Context context, BasicIO basicIO) throws Exception {
        SmartBrowz smartBrowz = catalystApp.smartBrowz();
        JSONObject browserDetails = smartBrowz.open();

        ChromeOptions options = new ChromeOptions();
        WebDriver driver = new RemoteWebDriver(
            new URL(browserDetails.getString("browser_http_url")),
            options
        );

        driver.get("https://example.com");
        String title = driver.getTitle();

        driver.quit();
        basicIO.write(new JSONObject().put("title", title));
        context.close();
    }
}
```

### Selenium — Node.js

```javascript
const { Builder } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');
const catalyst = require('zcatalyst-sdk-node');

module.exports = async (context, basicIO) => {
  const catalystApp = catalyst.initialize(context);
  const smartBrowz = catalystApp.smartBrowz();
  const browserDetails = await smartBrowz.open();

  const driver = await new Builder()
    .forBrowser('chrome')
    .usingServer(browserDetails.browser_http_url)
    .setChromeOptions(new chrome.Options())
    .build();

  await driver.get('https://example.com');
  const title = await driver.getTitle();

  await driver.quit();
  basicIO.write({ title });
  context.close();
};
```

### Selenium — Python

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def handler(catalyst_app, context, basic_io):
    smart_browz = catalyst_app.smart_browz()
    browser_details = smart_browz.open()

    options = Options()
    driver = webdriver.Remote(
        command_executor=browser_details["browser_http_url"],
        options=options
    )

    driver.get("https://example.com")
    title = driver.title

    driver.quit()
    basic_io.write({"title": title})
    context.close()
```

---

## Browser Logic Functions

Serverless functions with a browser session pre-initialized. No need to call `smartBrowz.open()`
— the browser is already connected when your function starts.

### Node.js (Playwright pre-initialized)

```javascript
// The browser and page are already available via browserData
module.exports = async (catalystApp, context, browserData) => {
  try {
    const input = JSON.parse(browserData.getArgument());
    const page = browserData.getPage(); // Pre-initialized Playwright page

    await page.goto(input.url || 'https://example.com');
    const title = await page.title();
    const screenshot = await page.screenshot({ encoding: 'base64' });

    context.close({ title, screenshot });
  } catch (error) {
    console.error('Browser Logic error:', error);
    context.close();
  }
};
```

### Java (Selenium pre-initialized)

```java
import org.openqa.selenium.WebDriver;

public class BrowserLogicFunction implements ZCBrowserFunction {
    public void runner(CatalystApp catalystApp, Context context, BrowserData browserData) throws Exception {
        String input = browserData.getArgument();
        WebDriver driver = browserData.getDriver(); // Pre-initialized Selenium WebDriver

        driver.get("https://example.com");
        String title = driver.getTitle();

        context.close(new JSONObject().put("title", title));
    }
}
```

### Constraints
- Max execution time: **15 minutes**
- Browser Logic functions are deployed like other Catalyst functions via `catalyst deploy`
- The pre-initialized browser session is scoped to the function execution — it is destroyed
  after the function completes

---

## Browser Grid (Early Access)

Dedicated browser infrastructure for high-volume or long-running browser automation workloads.
Provides persistent browser nodes rather than on-demand ephemeral sessions.

### Tier Configurations

| Tier | Nodes | Browsers/Node | Memory/Node | vCPU/Node | Use Case |
|------|-------|---------------|-------------|-----------|----------|
| **Basic** | 1 | 1 | 512 MB | 0.5 | Light testing, single-page scraping |
| **Light Advanced** | 2 | 2 | 1 GB | 1 | Moderate scraping, small-scale automation |
| **Moderate** | 4 | 4 | 2 GB | 2 | Production scraping, parallel test suites |
| **Heavy** | 8 | 8 | 4 GB | 4 | Large-scale automation, heavy parallel loads |

### Queue and Lifecycle
- **Queue duration**: Configurable — how long a request waits in the queue for an available
  browser slot before timing out
- **Grid states**: Creating → Active → Scaling → Stopping → Stopped
- **Alerts**: Configure alerts for queue saturation, node failures, and high resource usage

### Use Cases
- Running large Selenium/Playwright test suites in parallel
- High-volume web scraping with consistent performance
- Browser-based RPA workflows requiring dedicated resources
- Load testing web applications with real browsers

---

## PDF & Screenshot Generation

Generate PDFs and screenshots programmatically without managing a browser session.

### Input Methods
- **HTML string**: Pass raw HTML content directly
- **URL**: Provide a public URL to render
- **Templates**: Use a pre-configured LiquidJS template with dynamic data

### Output Formats
- **PDF**: Full-page PDF document
- **Screenshot**: PNG image (full page or viewport)

### Java SDK Example

```java
SmartBrowz smartBrowz = catalystApp.smartBrowz();

// PDF from URL
JSONObject pdfOptions = new JSONObject();
pdfOptions.put("format", "A4");
pdfOptions.put("print_background", true);
pdfOptions.put("landscape", false);

JSONObject navigationOptions = new JSONObject();
navigationOptions.put("wait_until", "networkidle0");
navigationOptions.put("timeout", 30000);

byte[] pdfBytes = smartBrowz.generatePdf(
    "https://example.com",
    pdfOptions,
    navigationOptions
);

// Screenshot from HTML
JSONObject screenshotOptions = new JSONObject();
screenshotOptions.put("full_page", true);
screenshotOptions.put("type", "png");

byte[] imageBytes = smartBrowz.captureScreenshot(
    "<html><body><h1>Hello</h1></body></html>",
    screenshotOptions
);
```

### Node.js SDK Example

```javascript
const smartBrowz = catalystApp.smartBrowz();

// PDF from URL
const pdfBuffer = await smartBrowz.generatePdf({
  url: 'https://example.com',
  pdf_options: {
    format: 'A4',
    print_background: true,
    landscape: false
  },
  navigation_options: {
    wait_until: 'networkidle0',
    timeout: 30000
  }
});

// Screenshot from HTML
const imageBuffer = await smartBrowz.captureScreenshot({
  html: '<html><body><h1>Hello</h1></body></html>',
  screenshot_options: {
    full_page: true,
    type: 'png'
  }
});
```

### Python SDK Example

```python
smart_browz = catalyst_app.smart_browz()

# PDF from URL
pdf_bytes = smart_browz.generate_pdf(
    url="https://example.com",
    pdf_options={
        "format": "A4",
        "print_background": True,
        "landscape": False
    },
    navigation_options={
        "wait_until": "networkidle0",
        "timeout": 30000
    }
)

# Screenshot from HTML
image_bytes = smart_browz.capture_screenshot(
    html="<html><body><h1>Hello</h1></body></html>",
    screenshot_options={
        "full_page": True,
        "type": "png"
    }
)
```

### Configuration Options

**`pdf_options`:**
- `format`: Page format — A4, Letter, Legal, Tabloid, A3, A5
- `print_background`: Include background graphics (default: false)
- `landscape`: Landscape orientation (default: false)
- `margin`: Object with `top`, `right`, `bottom`, `left` (CSS units)
- `scale`: Scale factor (0.1 to 2.0, default: 1)
- `header_template` / `footer_template`: HTML for headers/footers
- `page_ranges`: e.g., "1-3, 5"

**`page_options`:**
- `width`: Viewport width in pixels (default: 1280)
- `height`: Viewport height in pixels (default: 720)
- `device_scale_factor`: Device pixel ratio (default: 1)

**`screenshot_options`:**
- `full_page`: Capture entire scrollable page (default: false)
- `type`: "png" or "jpeg"
- `quality`: JPEG quality 0-100 (only for jpeg)
- `clip`: Object with `x`, `y`, `width`, `height` for partial capture

**`navigation_options`:**
- `wait_until`: "load", "domcontentloaded", "networkidle0", "networkidle2"
- `timeout`: Navigation timeout in milliseconds

---

## Templates

LiquidJS v10-based HTML templates for generating dynamic documents. Design templates in the
console with a visual editor.

### Template Syntax (LiquidJS v10)

**Variables:**
```html
<h1>Hello, {{ customer_name }}!</h1>
<p>Your order #{{ order_id }} has been confirmed.</p>
```

**Conditionals:**
```html
{% if status == "premium" %}
  <div class="premium-badge">Premium Member</div>
{% elsif status == "trial" %}
  <div class="trial-badge">Trial User</div>
{% else %}
  <div class="standard-badge">Standard Member</div>
{% endif %}
```

**Loops:**
```html
<table>
  {% for item in line_items %}
  <tr>
    <td>{{ item.name }}</td>
    <td>{{ item.quantity }}</td>
    <td>{{ item.price | currency }}</td>
  </tr>
  {% endfor %}
</table>
```

**Filters:**
```html
{{ created_at | date: "%B %d, %Y" }}
{{ price | divided_by: 100.0 | round: 2 }}
{{ description | truncate: 100 }}
{{ name | upcase }}
{{ email | downcase }}
```

**Case statements:**
```html
{% case priority %}
  {% when "high" %}
    <span style="color: red;">Urgent</span>
  {% when "medium" %}
    <span style="color: orange;">Normal</span>
  {% when "low" %}
    <span style="color: green;">Low Priority</span>
{% endcase %}
```

### Output Settings
- Choose PDF or Screenshot (PNG) output
- Configure page size, margins, orientation
- Set header/footer templates within the template configuration

### Template Lifecycle
- **Draft**: Template is editable and not available for API use
- **Published**: Template is locked and available for API use via template ID
- Publish a template to make it available; create a new draft version to edit

---

## Dataverse (Beta — US Data Center Only)

Business data enrichment APIs. Currently in beta and available only in the US data center.

### Available APIs

**Lead Enrichment**
- Input: Company name or domain
- Output: Company details (industry, size, revenue, location, social profiles)

**Tech Stack Finder**
- Input: Company domain
- Output: List of technologies used by the company (analytics, CMS, frameworks, etc.)

**Similar Companies**
- Input: Company name or domain
- Output: List of companies similar in industry, size, or technology usage

### Constraints
- **500 API calls per month** (across all Dataverse APIs combined)
- Beta feature — may change without notice
- Available only in the **US data center**

### Usage
```javascript
const smartBrowz = catalystApp.smartBrowz();
const dataverse = smartBrowz.dataverse();

// Lead Enrichment
const leadData = await dataverse.enrichLead({ domain: 'example.com' });

// Tech Stack
const techStack = await dataverse.getTechStack({ domain: 'example.com' });

// Similar Companies
const similar = await dataverse.getSimilarCompanies({ domain: 'example.com' });
```
