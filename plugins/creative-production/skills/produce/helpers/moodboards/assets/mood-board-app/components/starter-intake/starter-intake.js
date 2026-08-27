export const STARTER_INTAKE_PRESETS = Object.freeze({
  branding: {
    id: "make-logo-from-scratch",
    title: "First things first, what are we branding?",
    subtitle: "What's the product? Do you have an existing logo? Any additional art direction you want?",
    placeholder: "Type a brief, paste notes, or add a few directions...",
    suggestions: [
      {
        label: "Make 10 logos based on the letter R",
        text: "Make 10 distinct logo marks based on the letter R. Explore a wide range of styles: geometric, organic, luxury, playful, tech-forward, editorial, heritage, and minimalist.",
      },
      {
        label: "Make a wordmark for Kairos, a modern wellness spa",
        text: "Create a refined wordmark for Kairos, a modern wellness spa. Make it calm, elevated, spacious, and usable as a real brand mark.",
      },
      {
        label: "Create an identity for a sparkling tea brand",
        text: "Create an identity for a contemporary sparkling tea brand. Explore logo, color, type, and package-facing directions that feel fresh, crisp, and premium.",
      },
    ],
  },
  resize: {
    id: "template-assets",
    title: "Resize assets for different platforms",
    subtitle: "What reference asset are we resizing?",
    placeholder: "Type a brief, paste notes, or add a few directions...",
    suggestions: [
      {
        label: "Make this fit a YouTube banner",
        text: "Make this brand asset fit a YouTube banner. Preserve the main identity, rebuild the composition for the wide safe area, and keep it readable on desktop and mobile.",
      },
      {
        label: "Make this asset for all social platforms",
        text: "Make this asset for all major social platforms. Create crops and layout adaptations for feed, story, reel, short-video, and link-preview formats without losing the core idea.",
      },
      {
        label: "Turn this square launch graphic into a Story/Reel",
        text: "Turn a square launch graphic into a vertical Story/Reel version with a stronger top-to-bottom layout and room for platform UI.",
      },
    ],
    formats: [
      "Square 1:1",
      "Feed 4:5",
      "Story/Reel 9:16",
      "Carousel 4:5",
      "Landscape 16:9",
      "LinkedIn Post",
    ],
  },
});

export function createStarterIntake({
  preset = STARTER_INTAKE_PRESETS.branding,
  initialStep = "brief",
  initialValue = "",
  onClose,
  onSubmit,
} = {}) {
  const root = document.createElement("section");
  root.className = "cp-starter-intake";
  root.dataset.step = initialStep;
  root.setAttribute("aria-label", preset.title);
  root.innerHTML = `
    <div class="cp-starter-intake__panel">
      <div class="cp-starter-intake__copy">
        <h2 id="cp-starter-intake-title"></h2>
        <p class="cp-starter-intake__subtitle"></p>
      </div>
      <form class="cp-starter-intake__form" novalidate>
        <div class="cp-starter-intake__step" data-intake-step="brief">
          <div class="cp-starter-intake__composer">
            <div class="cp-starter-intake__attachments" aria-live="polite" hidden></div>
            <textarea aria-label="Starter brief"></textarea>
            <div class="cp-starter-intake__footer">
              <label class="cp-starter-intake__attach" aria-label="Attach files" title="Attach files">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" aria-hidden="true">
                  <path d="M12 5v14M5 12h14"></path>
                </svg>
                <input type="file" accept="image/png,image/jpeg,image/webp" multiple />
              </label>
            </div>
          </div>
          <div class="cp-starter-intake__suggestions" aria-label="Example use cases"></div>
        </div>
        <div class="cp-starter-intake__step cp-starter-intake__formats" data-intake-step="formats" hidden>
          <div class="cp-starter-intake__format-list" aria-label="Platform formats"></div>
        </div>
        <div class="cp-starter-intake__actions">
          <div class="cp-starter-intake__actions-inner">
            <div class="cp-starter-intake__buttons">
              <button class="cp-starter-intake__cancel" type="button">Back</button>
              <button class="cp-starter-intake__submit" type="submit">Continue</button>
            </div>
          </div>
        </div>
      </form>
    </div>
  `;

  const panel = root.querySelector(".cp-starter-intake__panel");
  const title = root.querySelector("h2");
  const subtitle = root.querySelector(".cp-starter-intake__copy p");
  const textarea = root.querySelector("textarea");
  const input = root.querySelector("input[type=file]");
  const attachments = root.querySelector(".cp-starter-intake__attachments");
  const suggestions = root.querySelector(".cp-starter-intake__suggestions");
  const formatList = root.querySelector(".cp-starter-intake__format-list");
  const cancel = root.querySelector(".cp-starter-intake__cancel");
  const submit = root.querySelector(".cp-starter-intake__submit");

  title.textContent = preset.title;
  subtitle.textContent = preset.subtitle;
  textarea.placeholder = preset.placeholder;
  textarea.value = initialValue;

  for (const suggestion of preset.suggestions || []) {
    const suggestionLabel = typeof suggestion === "string" ? suggestion : suggestion.label;
    const suggestionText = typeof suggestion === "string" ? suggestion : suggestion.text;
    const button = document.createElement("button");
    button.className = "cp-starter-intake__suggestion";
    button.type = "button";
    button.textContent = suggestionLabel;
    button.addEventListener("click", () => {
      textarea.value = suggestionText;
      clearError();
      textarea.focus();
    });
    suggestions.append(button);
  }

  for (const format of preset.formats || []) {
    const button = document.createElement("button");
    button.className = "cp-starter-intake__format";
    button.type = "button";
    button.setAttribute("aria-pressed", "false");
    button.innerHTML = `
      <span class="cp-starter-intake__format-icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 5v14M5 12h14"></path></svg>
      </span>
      <span>${format}</span>
    `;
    button.addEventListener("click", () => {
      const selected = button.getAttribute("aria-pressed") !== "true";
      button.setAttribute("aria-pressed", String(selected));
      button.querySelector("path").setAttribute("d", selected ? "m5 12.5 4.2 4.2L19 6.8" : "M12 5v14M5 12h14");
      clearError();
    });
    formatList.append(button);
  }

  function setStep(step) {
    const isFormats = step === "formats" && (preset.formats || []).length > 0;
    root.dataset.step = isFormats ? "formats" : "brief";
    root.querySelector('[data-intake-step="brief"]').hidden = isFormats;
    root.querySelector('[data-intake-step="formats"]').hidden = !isFormats;
    title.textContent = isFormats ? "Which sizes are we rebuilding?" : preset.title;
    subtitle.textContent = isFormats
      ? "Choose every platform format you want resized from the reference asset."
      : preset.subtitle;
    submit.textContent = "Continue";
    clearError();
  }

  function clearError() {
    root.classList.remove("has-error");
    root.querySelector(".cp-starter-intake__composer")?.classList.remove("is-warning", "is-warning-focus");
    subtitle.textContent = root.dataset.step === "formats"
      ? "Choose every platform format you want resized from the reference asset."
      : preset.subtitle;
    subtitle.classList.remove("is-warning");
    subtitle.removeAttribute("role");
  }

  function showError(message) {
    root.classList.add("has-error");
    root.querySelector(".cp-starter-intake__composer")?.classList.add("is-warning");
    subtitle.textContent = message;
    subtitle.classList.add("is-warning");
    subtitle.setAttribute("role", "alert");
  }

  function renderAttachments() {
    attachments.replaceChildren();
    const files = [...(input.files || [])];
    attachments.hidden = files.length === 0;
    for (const file of files) {
      const chip = document.createElement("span");
      chip.className = "cp-starter-intake__attachment";
      chip.textContent = file.name;
      attachments.append(chip);
    }
  }

  cancel.addEventListener("click", () => {
    if (root.dataset.step === "formats") {
      setStep("brief");
      textarea.focus();
      return;
    }
    onClose?.();
  });
  input.addEventListener("change", () => {
    clearError();
    renderAttachments();
  });
  textarea.addEventListener("input", clearError);
  textarea.addEventListener("focus", () => {
    if (root.classList.contains("has-error")) {
      root.querySelector(".cp-starter-intake__composer")?.classList.add("is-warning-focus");
    }
  });
  textarea.addEventListener("blur", () => {
    root.querySelector(".cp-starter-intake__composer")?.classList.remove("is-warning", "is-warning-focus");
  });
  root.querySelector("form").addEventListener("submit", (event) => {
    event.preventDefault();
    const files = [...(input.files || [])];
    const notes = textarea.value.trim();
    if (root.dataset.step === "brief" && !notes && files.length === 0) {
      showError("Add notes or attach a reference to continue");
      textarea.focus();
      return;
    }
    if (root.dataset.step === "brief" && preset.formats?.length) {
      setStep("formats");
      return;
    }
    const formats = [...formatList.querySelectorAll('[aria-pressed="true"]')].map((node) => node.innerText.trim());
    if (root.dataset.step === "formats" && formats.length === 0) {
      showError("Choose at least one platform format");
      return;
    }
    onSubmit?.({ preset, notes, files, formats });
  });

  setStep(initialStep);
  return {
    element: root,
    modal: panel,
    setStep,
    destroy() {
      root.remove();
    },
  };
}
export function mountStarterIntake(container, options = {}) {
  if (!(container instanceof Element)) {
    throw new TypeError("mountStarterIntake requires a DOM element container.");
  }
  const component = createStarterIntake(options);
  container.replaceChildren(component.element);
  return component;
}
