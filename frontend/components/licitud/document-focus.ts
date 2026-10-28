export const documentNavigationButtonClass =
  "inline-flex min-h-11 max-w-full items-center rounded-md border border-blue-300 bg-blue-50 px-3 py-2 text-left font-semibold text-blue-900 whitespace-normal hover:bg-blue-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-blue-50";

/** Moves within a document without changing the workspace route or its drafts. */
export function focusDocumentSection(target: HTMLElement | null) {
  if (!target) return;
  const header = target.closest(".connected-app")?.querySelector("header");
  target.style.scrollMarginTop = `${(header?.getBoundingClientRect().height ?? 0) + 12}px`;
  target.focus({ preventScroll: true });
  target.scrollIntoView({ block: "start" });
}

export const documentDisclosureClass =
  "min-h-11 max-w-full list-inside cursor-pointer rounded-md border border-blue-300 bg-blue-50 px-3 py-2 font-semibold text-blue-900 whitespace-normal hover:bg-blue-100 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-700";
