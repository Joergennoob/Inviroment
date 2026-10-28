import { explainPlacement } from "@/lib/words";

export default function PlaceNote({
  featureName,
  sourceName,
  recordId,
  sourceUrl,
  retrieved,
  note,
  layer,
}: {
  featureName: string;
  sourceName: string;
  recordId: string;
  sourceUrl: string;
  retrieved: string;
  note: string;
  layer?: string;
}) {
  const explained = explainPlacement({ featureName, sourceName, recordId, note, layer });
  return (
    <div className="place">
      <p>
        <strong>Hvorfor ligger dette her? </strong>
        {explained.plain}
      </p>
      <details className="tech">
        <summary>For journalister: tekniske detaljer</summary>
        <p>
          {note} {sourceName}, post {recordId}. <a href={sourceUrl}>Kildelenke</a>. Hentet {retrieved}.
        </p>
      </details>
    </div>
  );
}
