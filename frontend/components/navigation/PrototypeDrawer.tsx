"use client";
import { useEffect, useRef, type ReactNode } from "react";
import { createPortal } from "react-dom";

export function PrototypeDrawer({
  open,
  label,
  className,
  close,
  children,
}: {
  open: boolean;
  label: string;
  className: string;
  close: () => void;
  children: ReactNode;
}) {
  const panel = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!open) return;
    const background = document.querySelector<HTMLElement>(".prototype-app");
    const wasInert = background?.inert ?? false;
    const overflow = document.body.style.overflow;
    if (background) background.inert = true;
    document.body.style.overflow = "hidden";
    const buttons = () =>
      Array.from(
        panel.current?.querySelectorAll<HTMLElement>(
          'button:not([disabled]), a[href], select, input, textarea, [tabindex="0"]'
        ) ?? []
      ).filter((item) => item.getClientRects().length > 0);
    buttons()[0]?.focus();
    const keyboard = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        event.stopImmediatePropagation();
        close();
      } else if (event.key === "Tab") {
        const items = buttons();
        const first = items[0];
        const last = items[items.length - 1];
        if (!first) {
          event.preventDefault();
          panel.current?.focus();
          return;
        }
        if (
          event.shiftKey &&
          (document.activeElement === first || !panel.current?.contains(document.activeElement))
        ) {
          event.preventDefault();
          last.focus();
        } else if (
          !event.shiftKey &&
          (document.activeElement === last || !panel.current?.contains(document.activeElement))
        ) {
          event.preventDefault();
          first.focus();
        }
      }
    };
    window.addEventListener("keydown", keyboard, true);
    return () => {
      window.removeEventListener("keydown", keyboard, true);
      if (background) background.inert = wasInert;
      document.body.style.overflow = overflow;
    };
  }, [open, close]);
  return createPortal(
    <div
      hidden={!open}
      className="prototype-drawer-backdrop"
      onPointerDown={(event) => {
        if (event.target === event.currentTarget) {
          event.preventDefault();
          close();
        }
      }}
    >
      <div
        ref={panel}
        role="dialog"
        aria-modal="true"
        aria-label={label}
        tabIndex={-1}
        className={`prototype-drawer ${className}`}
      >
        {children}
      </div>
    </div>,
    document.body
  );
}
