import { DataProvenance } from "@/lib/api";

type Props = {
  metadata: DataProvenance;
};

export function MetadataNotice({ metadata }: Props) {
  if (!metadata.is_fallback && metadata.data_complete) {
    return null;
  }

  return (
    <section className="notice notice-warning">
      <h3>Data provenance note</h3>
      <p>
        Source: <strong>{metadata.data_source}</strong>. This response may have incomplete coverage.
      </p>
      {metadata.note ? <p>{metadata.note}</p> : null}
    </section>
  );
}
