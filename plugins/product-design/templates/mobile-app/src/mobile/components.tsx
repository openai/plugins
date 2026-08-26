import { useEffect, useState } from "react";
import { KeyboardInput, useKeyboard } from "./Keyboard";
import { useMobileDevice } from "./Device";

export function StatusBar() {
  const [now, setNow] = useState(() => new Date());
  const { device } = useMobileDevice();

  useEffect(() => {
    const syncToMinute = window.setTimeout(() => {
      setNow(new Date());
    }, (60 - now.getSeconds()) * 1000 - now.getMilliseconds());
    const interval = window.setInterval(() => setNow(new Date()), 60_000);

    return () => {
      window.clearTimeout(syncToMinute);
      window.clearInterval(interval);
    };
  }, [now]);

  return (
    <div className="status-bar" aria-label="Device status bar">
      <span className="status-time" data-testid="status-time">
        {formatStatusTime(now)}
      </span>
      <div className="status-indicators" aria-hidden="true">
        <StatusIndicators platform={device.platform} />
      </div>
    </div>
  );
}

export function HomeIndicator() {
  const { device } = useMobileDevice();
  const keyboard = useKeyboard();

  if (device.platform === "android") {
    if (keyboard.visible) return null;

    return (
      <img
        className="android-navigation-bar"
        data-testid="android-navigation-bar"
        src="/assets/android/navigation-bar.svg"
        alt=""
        aria-hidden="true"
        draggable={false}
      />
    );
  }

  return (
    <svg
      className="home-indicator-svg"
      data-testid="home-indicator"
      width="393"
      height="34"
      viewBox="0 0 393 34"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <rect x="129.5" y="21" width="134" height="5" rx="2.5" fill="black" />
    </svg>
  );
}

export function MobileTextField({
  id,
  label,
  placeholder,
  testId,
}: {
  id: string;
  label: string;
  placeholder?: string;
  testId?: string;
}) {
  return (
    <label className="mobile-field" htmlFor={id}>
      <span className="field-label">{label}</span>
      <KeyboardInput id={id} data-testid={testId} placeholder={placeholder} />
    </label>
  );
}

function formatStatusTime(date: Date) {
  const hours = date.getHours();
  const minutes = String(date.getMinutes()).padStart(2, "0");

  return `${hours % 12 || 12}:${minutes}`;
}

function StatusIndicators({ platform }: { platform: "ios" | "android" }) {
  return (
    <img
      className="status-indicator-svg"
      data-testid="status-indicators"
      data-platform={platform}
      src={
        platform === "android"
          ? "/assets/status/status-icons.svg"
          : "/assets/status/ios-status-icons.svg"
      }
      alt=""
      aria-hidden="true"
      draggable={false}
    />
  );
}
