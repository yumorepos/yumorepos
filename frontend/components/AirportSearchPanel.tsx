"use client";

import { FormEvent } from "react";
import { Airport } from "@/lib/api";
import { formatLocation } from "@/lib/format";

type Props = {
  query: string;
  onQueryChange: (value: string) => void;
  airports: Airport[];
  selectedOrigin: string;
  onSelectOrigin: (iata: string) => void;
  onSearch: () => void;
  isSearching: boolean;
};

export function AirportSearchPanel({
  query,
  onQueryChange,
  airports,
  selectedOrigin,
  onSelectOrigin,
  onSearch,
  isSearching,
}: Props) {
  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSearch();
  };

  return (
    <section className="panel">
      <h2>Select origin airport</h2>
      <p className="muted">Search by IATA, city, or airport name. Then choose one airport to explore connected routes.</p>

      <form className="search-form" onSubmit={handleSubmit}>
        <input
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          placeholder="Try JFK, SFO, or Dallas"
          aria-label="Search airports"
        />
        <button type="submit" disabled={isSearching || query.trim().length < 1}>
          {isSearching ? "Searching..." : "Search airports"}
        </button>
      </form>

      <div className="airport-list">
        {airports.map((airport) => (
          <button
            key={airport.iata}
            className={`airport-item ${selectedOrigin === airport.iata ? "selected" : ""}`}
            type="button"
            onClick={() => onSelectOrigin(airport.iata)}
          >
            <strong>{airport.iata}</strong>
            <span>{airport.airport_name}</span>
            <small>{formatLocation(airport.city, airport.state, airport.country)}</small>
          </button>
        ))}
      </div>
    </section>
  );
}
