"use client";

import { useState } from "react";
import type { Claim } from "@/lib/types";
import { STATUS_WORD } from "@/lib/stage";

export default function SourceChip({ claim }: { claim: Claim }) {
  const [open, setOpen] = useState(false);
  const word = STATUS_WORD[claim.status] ?? claim.status;
  return (
    <span className="srcchip">
      <i className={`dot ${claim.status}`} title={word} />
      <button type="button" onClick={() => setOpen((value) => !value)} aria-expanded={open}>
        Kilde
      </button>
      {open ? (
        <span className="srcpop" role="dialog">
          <strong>{word}</strong>
          {claim.sources.map((source) => (
            <span key={source.url + source.title} className="srcitem">
              <a href={source.url} target="_blank" rel="noreferrer">
                {source.title}
              </a>
              <span>Hentet {source.retrieved}</span>
              {source.archive_url ? (
                <a href={source.archive_url} target="_blank" rel="noreferrer">
                  Arkivkopi
                </a>
              ) : (
                <span>{source.archive_note}</span>
              )}
            </span>
          ))}
        </span>
      ) : null}
    </span>
  );
}
