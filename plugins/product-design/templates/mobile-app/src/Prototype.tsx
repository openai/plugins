import { MobileScroll } from "./mobile";

// Build app-specific screens and flows in this file. The surrounding mobile
// runtime is template-owned and intentionally lives outside this component.
export default function Prototype() {
  return (
    <MobileScroll className="app-screen">
      <main className="screen-content blank-canvas" data-testid="blank-canvas" aria-label="Blank prototype canvas" />
    </MobileScroll>
  );
}
