export function formatLocation(city: string | null, state: string | null, country: string): string {
  const cityPart = city ?? "Unknown city";
  const statePart = state ? `, ${state}` : "";
  return `${cityPart}${statePart}, ${country}`;
}

export function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return "Not available";
  }

  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 }).format(value);
}

export function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return "Not available";
  }

  return `${(value * 100).toFixed(1)}%`;
}

export function formatMonth(year: number, month: number): string {
  return new Date(Date.UTC(year, month - 1, 1)).toLocaleString("en-US", {
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  });
}
