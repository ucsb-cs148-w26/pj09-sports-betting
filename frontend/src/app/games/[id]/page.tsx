import GameClient from './GameClient'

type Props = {
  params: Promise<{
    id: string
  }>
}

export default async function GamePage({ params }: Props) {
  const p = await params;
  return <GameClient id={p.id} />
}