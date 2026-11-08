export const dynamic = 'force-dynamic';
export default async function QueryPage({ searchParams }) {
  const query = await searchParams;
  const term = typeof query.term === 'string' ? query.term : '';
  const tags = Array.isArray(query.tag) ? query.tag : query.tag ? [query.tag] : [];
  return <section><h1>NEXT_QUERY</h1><p data-testid="query-term">{term}</p><p data-testid="query-tags">{tags.join('|')}</p></section>;
}
