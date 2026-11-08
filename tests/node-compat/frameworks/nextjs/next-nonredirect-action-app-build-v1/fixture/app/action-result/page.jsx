export const dynamic = 'force-dynamic';
export default async function ActionResult({ searchParams }) {
  const query = await searchParams;
  return <section><h1>NEXT_ACTION_RESULT</h1><p data-testid="action-result">{typeof query.value === 'string' ? query.value : ''}</p></section>;
}
