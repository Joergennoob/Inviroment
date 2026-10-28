import Link from "next/link";
import LobbyView from "@/components/LobbyView";
import roster from "@/data/lobby/roster.json";

export default function LobbyPage() {
  return (
    <div className="page">
      <p>
        <Link href="/">Kart</Link>
        {" · "}
        <Link href="/oversikt/">Rangering</Link>
        {" · "}
        <Link href="/network/">Nettverk</Link>
      </p>
      <h1>Lobbyister</h1>
      <p>
        Firma og interne lobbyister som i 2025 er registrert for selskapene bak de ti problemene. Listen viser hvem som
        jobber der, hvilke klienter registreringen nevner, og penger der et skjema er lest.
      </p>
      <LobbyView roster={roster} />
    </div>
  );
}
