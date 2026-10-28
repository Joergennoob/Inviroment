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
        Her ser du folk som jobber for selskapene og prøver å påvirke lovene i California. Du kan filtrere på problem.
        Grønt merke for «jobber for begge sider» brukes bare når registeret viser både et forurensende selskap og en miljøgruppe. Det merket er ikke i bruk nå.
      </p>
      <LobbyView roster={roster} />
    </div>
  );
}
