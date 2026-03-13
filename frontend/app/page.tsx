"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { AirportSearchPanel } from "@/components/AirportSearchPanel";
import { MetadataNotice } from "@/components/MetadataNotice";
import { RouteExploreCard } from "@/components/RouteExploreCard";
import { AirportSearchResponse, RouteExploreResponse, exploreRoutes, searchAirports } from "@/lib/api";

export default function HomePage() {
  const [query, setQuery] = useState("JFK");
  const [selectedOrigin, setSelectedOrigin] = useState<string>("JFK");

  const [airportData, setAirportData] = useState<AirportSearchResponse | null>(null);
  const [routesData, setRoutesData] = useState<RouteExploreResponse | null>(null);

  const [searchError, setSearchError] = useState<string | null>(null);
  const [routesError, setRoutesError] = useState<string | null>(null);

  const [isSearching, setIsSearching] = useState(false);
  const [isLoadingRoutes, setIsLoadingRoutes] = useState(false);

  const loadAirports = useCallback(async () => {
    setIsSearching(true);
    setSearchError(null);

    try {
      const data = await searchAirports(query.trim());
      setAirportData(data);
      if (data.results.length > 0 && !data.results.find((airport) => airport.iata === selectedOrigin)) {
        setSelectedOrigin(data.results[0].iata);
      }
    } catch (error) {
      setSearchError(error instanceof Error ? error.message : "Airport search failed.");
      setAirportData(null);
    } finally {
      setIsSearching(false);
    }
  }, [query, selectedOrigin]);

  useEffect(() => {
    void loadAirports();
  }, [loadAirports]);

  useEffect(() => {
    if (!selectedOrigin) {
      setRoutesData(null);
      return;
    }

    const loadRoutes = async () => {
      setIsLoadingRoutes(true);
      setRoutesError(null);

      try {
        const data = await exploreRoutes(selectedOrigin);
        setRoutesData(data);
      } catch (error) {
        setRoutesError(error instanceof Error ? error.message : "Route exploration failed.");
        setRoutesData(null);
      } finally {
        setIsLoadingRoutes(false);
      }
    };

    void loadRoutes();
  }, [selectedOrigin]);

  const hasSearchResults = useMemo(() => (airportData?.results.length ?? 0) > 0, [airportData?.results.length]);

  return (
    <main className="page-shell">
      <section className="hero">
        <p className="eyebrow">Flight Price Intelligence Lab</p>
        <h1>Route Explorer</h1>
        <p>
          Evaluate route attractiveness, pricing signals, and reliability in one decision-ready workspace designed for airline and
          travel analytics conversations.
        </p>
      </section>

      <AirportSearchPanel
        query={query}
        onQueryChange={setQuery}
        airports={airportData?.results ?? []}
        selectedOrigin={selectedOrigin}
        onSelectOrigin={setSelectedOrigin}
        onSearch={loadAirports}
        isSearching={isSearching}
      />

      {searchError ? <p className="status error">Airport search error: {searchError}</p> : null}
      {!isSearching && !searchError && !hasSearchResults ? <p className="status">No airports matched your query.</p> : null}

      <section className="panel">
        <div className="panel-header">
          <h2>Routes from {selectedOrigin || "—"}</h2>
          <p className="muted">Ranked routes with latest score, fare insight, and reliability cues.</p>
        </div>

        {isLoadingRoutes ? <p className="status">Loading routes…</p> : null}
        {routesError ? <p className="status error">Route explorer error: {routesError}</p> : null}
        {!isLoadingRoutes && !routesError && routesData && routesData.routes.length === 0 ? (
          <p className="status">No routes available for this origin yet.</p>
        ) : null}

        {routesData ? <MetadataNotice metadata={routesData.metadata} /> : null}

        <div className="route-grid">
          {routesData?.routes.map((route) => (
            <RouteExploreCard key={route.destination.iata} origin={routesData.origin} route={route} />
          ))}
        </div>
      </section>
    </main>
  );
}
