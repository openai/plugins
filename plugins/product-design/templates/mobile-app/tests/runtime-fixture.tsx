import { StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  BottomSheet,
  Carousel,
  FlowStack,
  KeyboardInput,
  MobileRuntime,
  MobileScroll,
  type FlowScreen,
} from "../src/mobile";
import "../src/styles.css";
import "./runtime-fixture.css";

function CarouselFixture() {
  const [tapCount, setTapCount] = useState(0);
  const [sheetOpen, setSheetOpen] = useState(false);

  return (
    <MobileRuntime>
      <MobileScroll className="fixture-screen">
        <main className="fixture-content">
          <h1>Runtime fixture</h1>
          <button className="sheet-trigger" type="button" onClick={() => setSheetOpen(true)}>
            Open sheet
          </button>
          <Carousel
            ariaLabel="Featured cards"
            className="fixture-carousel"
            contentClassName="fixture-carousel-track"
          >
            {Array.from({ length: 7 }, (_, index) => (
              <button
                className="carousel-card"
                type="button"
                onClick={() => setTapCount((count) => count + 1)}
                key={index}
              >
                Card {index + 1}
              </button>
            ))}
          </Carousel>
          <output data-testid="tap-count">{tapCount}</output>
          <div className="fixture-tall-content">Scrollable parent content</div>
        </main>
      </MobileScroll>
      <BottomSheet
        open={sheetOpen}
        onOpenChange={setSheetOpen}
        title="Animated sheet"
        description="Exit motion regression fixture."
      >
        <p>Sheet content</p>
      </BottomSheet>
    </MobileRuntime>
  );
}

function KeyboardFixture() {
  const screen: FlowScreen = {
    id: "keyboard",
    footerHeight: 84,
    footer: () => (
      <div className="keyboard-footer">
        <KeyboardInput aria-label="Message" placeholder="Message" />
      </div>
    ),
    render: () => (
      <MobileScroll className="fixture-screen">
        <main className="fixture-content fixture-tall-content">Keyboard fixture</main>
      </MobileScroll>
    ),
  };

  return (
    <MobileRuntime>
      <FlowStack initial={screen} />
    </MobileRuntime>
  );
}

function stackedScreen(level: number): FlowScreen {
  return {
    id: `flow-level-${level}`,
    headerHeight: 56,
    header: (flow) => (
      <div className="flow-fixture-header">
        <button type="button" onClick={flow.pop}>‹ Back</button>
        <strong>Level {level}</strong>
        <span />
      </div>
    ),
    footerHeight: 64,
    footer: (flow) => (
      <div className="flow-fixture-footer">
        <button type="button" onClick={flow.pop}>Done</button>
      </div>
    ),
    render: (flow) => (
      <MobileScroll className="fixture-screen">
        <main className="fixture-content">
          <h1>{level === 2 ? "Screen stacking works" : `Nested view level ${level}`}</h1>
          {level < 4 ? (
            <button type="button" onClick={() => flow.push(stackedScreen(level + 1))}>
              Push level {level + 1}
            </button>
          ) : null}
        </main>
      </MobileScroll>
    ),
  };
}

function FlowFixture() {
  const screen: FlowScreen = {
    id: "flow-root",
    footerHeight: 84,
    footer: () => (
      <div className="keyboard-footer">
        <KeyboardInput aria-label="Flow message" placeholder="Message" />
      </div>
    ),
    render: (flow) => (
      <MobileScroll className="fixture-screen">
        <main className="fixture-content">
          <h1>Flow root</h1>
          <button type="button" onClick={() => flow.push(stackedScreen(2))}>
            Push level 2
          </button>
        </main>
      </MobileScroll>
    ),
  };

  return (
    <MobileRuntime>
      <FlowStack initial={screen} />
    </MobileRuntime>
  );
}

const fixture = new URLSearchParams(window.location.search).get("fixture");
const fixtureElement =
  fixture === "keyboard"
    ? <KeyboardFixture />
    : fixture === "flow"
      ? <FlowFixture />
      : <CarouselFixture />;

createRoot(document.getElementById("root")!).render(
  <StrictMode>{fixtureElement}</StrictMode>,
);
